> [Receiving-session note, 2026-09-13, D-050-R002: owner-returned deep-research result,
> received via the D-050 channel and archived verbatim below as a DISCOVERY AID. It is NOT
> provenance: no citation chain may terminate here; every load-bearing claim must be captured
> from the official source under the normal (print/PDF-class where applicable) discipline
> before encoding. The companion PDF and evidence ZIP remain with the owner (thin client).
> Queue stamps: docs/RESEARCH_REQUESTS.md. Received by the wave-3 build session.]

# NYC Buildability: answers to the five research requests

Research date: September 13, 2026. Prepared for the owner of nyc-buildability.

## What the evidence supports

I read the requested RESEARCH_REQUESTS.md on branch candidate/D-024-mrl-option-b, file blob 69d79cadaf41d5f73adab36aba173ae6036f4862. This report addresses all five entries in that snapshot. It is a research handoff, not an owner decision, professional interpretation, or G6 approval. No repository files or queue statuses were changed.

The central finding is that the missing rules are mostly retrievable, but several shortcuts in the proposed rule structure would be wrong. Standard R6-R12 envelopes and the optional sky-exposure-plane system are separate routes. C4-6 has an R10 residential equivalent. Commercial overlays have explicit exceptions to underlying residential bulk. Qualifying residential sites have several independent routes and special-district exclusions. LION measures pavement width; DCM describes mapped widths, but the precise field-level measurement convention remains undocumented in the sources recovered here.

| Request | Research result | Remaining verification target |
|---|---|---|
| RQ-001: residential geometry | Core section map and dependencies located | Capture complete sections, tables, footnotes, diagrams and applicable geographic overrides before encoding |
| RQ-002: commercial structure | FAR tables, overlay rules, equivalents and suffix rule located | Capture use-specific tables and exceptions; correct C4-6 example |
| RQ-003: qualifying residential site | Complete definition found in current official HTML, including its final affordability paragraph | Original HTML is in the evidence archive; print/PDF completeness remains a normal-capture task |
| RQ-004: special districts | 59 current chapter families inventoried; geography and bulk effects identified | Resolve index inconsistencies and distinguish activity measurements from legal applicability |
| RQ-005: street-width provenance | Exact ZIP and internal file verified; current LION definition visually verified | DCM's exact field-level measurement convention remains open |

The sources were the city's Zoning Resolution, DCP's live download pages, original metadata PDFs and ZIP contents, and DCP data. Current text matters: the wide-street definition shows an amendment on March 26, 2026. Treating the whole exercise as a frozen December 2024 text would miss later changes. The source archive preserves downloaded bytes and checksums; it does not certify that the project's prescribed capture process has been satisfied.

## RQ-001: residential geometry and height mechanics

### Choose the governing route before calculating an envelope

[§23-40, HEIGHT AND SETBACK REGULATIONS](https://zr.planning.nyc.gov/article-ii/chapter-3/23-40) routes R6-R12 residences into §23-43, with permitted obstructions under §23-41 and geographic modifications under §23-44. The optional sky-exposure-plane route sits in §23-73. It is not the universal rule for every mid- or high-density district.

[§23-731, Applicability](https://zr.planning.nyc.gov/article-ii/chapter-3/23-731) limits that optional route to R6-R10 without a letter suffix, then expressly excludes R6-1, R6-2, R7-3 and R9-1, R8 in Manhattan Community District 9 north of West 125th Street, and Limited Height Districts. R11/R12 and contextual lettered districts do not acquire this option merely because they are higher density.

For commercial districts, also capture [§35-81, Special Provisions for Sky Exposure Plane Buildings](https://zr.planning.nyc.gov/article-iii/chapter-5/35-81) and the governing commercial height provisions. A residential equivalent identifies the applicable residential family; it does not authorize bypassing Article III's mixed-building rules.

### Core capture map

The district column below distinguishes a section's displayed district family from restrictions inside its text. “Width” identifies a direct wide/narrow distinction or another street-geometry dependency. Definitions are indexed immediately after the table.

| Section and exact title | District scope | Width / geometry dependency |
|---|---|---|
| [23-41 Permitted Obstructions](https://zr.planning.nyc.gov/article-ii/chapter-3/23-41) | Residence districts | Parent obstruction map; follow all three children |
| [23-411 General permitted obstructions](https://zr.planning.nyc.gov/article-ii/chapter-3/23-411) | R1-R12 | Object-specific dimensions, roof position, area and transparency; no blanket height bonus |
| [23-412 Additional permitted obstructions](https://zr.planning.nyc.gov/article-ii/chapter-3/23-412) | R1-R12; separate low/high-density provisions | Mechanical/bulkhead street-line offsets differ: 25 feet narrow, 20 feet wide limits on required distancing; coverage and equipment-height tests |
| [23-413 Permitted obstructions in certain districts](https://zr.planning.nyc.gov/article-ii/chapter-3/23-413) | R1-R12, conditional on envelope | Dormers, roof slopes and front setback penetration; capture percentage and taper tests |
| [23-43 Height and Setback Requirements in R6 Through R12 Districts](https://zr.planning.nyc.gov/article-ii/chapter-3/23-43) | R6-R12 | Standard route; base-plane measurement and child sections |
| [23-431 Street wall location requirements](https://zr.planning.nyc.gov/article-ii/chapter-3/23-431) | R6-R12; special R6B/R7B/R8B rules | Generally 70% within 8 feet on wide streets or 10 feet on narrow streets; adjacency and large-lot alternatives |
| [23-432 Height and setback requirements](https://zr.planning.nyc.gov/article-ii/chapter-3/23-432) | R6-R12, including lettered/numerical table rows | Some rows distinguish portions within 100 feet of a wide street from other portions; housing-program columns also change limits |
| [23-433 Standard setback regulations](https://zr.planning.nyc.gov/article-ii/chapter-3/23-433) | R6-R12 | Standard setback 10 feet wide / 15 feet narrow; reductions and geometric exceptions |
| [23-434 Height and setback modifications for eligible sites](https://zr.planning.nyc.gov/article-ii/chapter-3/23-434) | R6-R12 without a letter suffix | Transportation frontage, irregular lot dimensions/angles/slope, large lots or entire blocks; eligibility and historical conditions |
| [23-435 Tower regulations](https://zr.planning.nyc.gov/article-ii/chapter-3/23-435) | R9-R12 except R9A, R9X, R10A, R11A | Alternative maximum-height treatment; tower coverage and height bands, plus §23-441 |
| [23-436 Additional height and setback provisions](https://zr.planning.nyc.gov/article-ii/chapter-3/23-436) | R6-R12 | Existing buildings, through/corner lots, historic districts, sidewalk widenings and street-wall exceptions |
| [23-44 Special Provisions for Certain Areas](https://zr.planning.nyc.gov/article-ii/chapter-3/23-44) | Geographic applicability | Parent map for the following three sections |
| [23-441 Special tower provisions](https://zr.planning.nyc.gov/article-ii/chapter-3/23-441) | Specified R9/R10 and R9D/R10X cases | Wide-street frontage, short/long block dimensions, tower coverage, tower-on-base and park adjacency |
| [23-442 Special provisions for certain community districts](https://zr.planning.nyc.gov/article-ii/chapter-3/23-442) | Named Manhattan/Brooklyn areas | Location-based restrictions and geometry; do not reduce to district designation alone |
| [23-443 Special provisions in other geographies](https://zr.planning.nyc.gov/article-ii/chapter-3/23-443) | Named situations across R1-R12 | Park frontage, transportation adjacency, Limited Height Districts and district-boundary transitions |
| [23-73 Special Provisions for Sky Exposure Plane Buildings](https://zr.planning.nyc.gov/article-ii/chapter-3/23-73) | Optional route subject to §23-731 | Changes the governing bulk system, not only the height formula |
| [23-731 Applicability](https://zr.planning.nyc.gov/article-ii/chapter-3/23-731) | R6-R10 without letters; express exclusions | Route gate; narrower than the district family in the title |
| [23-732 Floor area ratio and open space ratio in R6 through R9 Districts](https://zr.planning.nyc.gov/article-ii/chapter-3/23-732) | Eligible R6-R9 | Height-factor/open-space mechanics; capture with the optional route |
| [23-733 Floor area ratios in R9 and R10 Districts](https://zr.planning.nyc.gov/article-ii/chapter-3/23-733) | Eligible R9/R10 | FAR consequences of the elected route and tower cross-references |
| [23-734 Permitted obstructions in open space](https://zr.planning.nyc.gov/article-ii/chapter-3/23-734) | Eligible sky-exposure-plane buildings | Open-space obstruction rules; distinct from roof-height obstructions |
| [23-735 Special yard, court and other area regulations](https://zr.planning.nyc.gov/article-ii/chapter-3/23-735) | Eligible sky-exposure-plane buildings | Yard equivalents, lot coverage and building/window separation |
| [23-736 Special height and setback regulations for sky exposure plane buildings](https://zr.planning.nyc.gov/article-ii/chapter-3/23-736) | Eligible R6-R10 | Plane origin, slope, front wall, initial setback and alternate front open area all matter |
| [23-737 Tower regulations](https://zr.planning.nyc.gov/article-ii/chapter-3/23-737) | Eligible R9/R10; §23-441 carve-outs | 10-foot wide / 15-foot narrow tower setbacks; lot-area coverage and park proximity |
| [23-738 Height limitations for narrow buildings or enlargements](https://zr.planning.nyc.gov/article-ii/chapter-3/23-738) | R7-2, R8, R9, R10 in this route | Street wall under 45 feet; actual street width can determine cap, with corner/through-lot and distance exceptions |
| [23-739 Limited Height Districts](https://zr.planning.nyc.gov/article-ii/chapter-3/23-739) | LH-1, LH-1A, LH-2, LH-3 | Named caps and housing exceptions; reconcile with §23-731's exclusion before application |

### Numbers that prevent common implementation errors

Under §23-433, the standard front setback is 10 feet on a wide street and 15 feet on a narrow street. A street wall set back from the street line can reduce that requirement one-for-one, but generally not below seven feet. Recesses, courts, portions more than 50 feet from a street line, angular relationships and dormers introduce additional qualifications. The setback must occur within the allowed base-height interval; it is not simply a horizontal offset at ground level.

§23-432's table has five numeric columns: minimum base height, standard maximum base/building heights, and maximum base/building heights for qualifying affordable or senior housing. Its footnotes classify building portions, not necessarily an entire lot. For example, R6's wide-street-proximate standard envelope uses 65/75 feet maximum base/building height, while the applicable narrow-street row uses 45/55. R12 has 155/325 for standard housing and 155/395 for qualifying affordable/senior housing. These examples do not replace the complete table or its footnotes.

| Optional sky-plane route under §23-736 | Narrow street | Wide street |
|---|---|---|
| Paragraph (a): initial setback distance | 20 feet | 15 feet |
| Paragraph (a): plane slope, vertical:horizontal | 2.7:1 | 5.6:1 |
| Paragraph (b): alternate front open area depth | 15 feet | 10 feet |
| Paragraph (b): alternate plane slope, vertical:horizontal | 3.7:1 | 7.6:1 |

The plane starts at 60 feet for R6/R7 and 85 feet for R8-R10. Paragraph (a)'s front-wall limit is additionally the lesser of 60 feet/six stories or 85 feet/nine stories, respectively. The alternate paragraph (b) is unavailable in R9/R10 where more than 25% of the building's floor area is residential. Keep the elected route, frontage, plane origin and story limit together.

§23-434 is an eligible-site alternative; “large” or “irregular” cannot be inferred from a label. The section tests dimensions, angles, slope, transportation frontage, dates, lot assembly and existing conditions. §23-435 permits a tower alternative to §23-432's maximum building-height requirement, subject to coverage and other controls; do not translate that into an unconditional claim of unlimited permissible height.

§23-436(a)'s provision for an existing building enlarged by up to one story or 15 feet addresses street-wall location compliance. It is not an automatic 15-foot addition to every otherwise applicable height cap.

### Defined-term dependency index

The general definitions below are in [§12-10, DEFINITIONS](https://zr.planning.nyc.gov/article-i/chapter-2/12-10). These are navigation and implementation notes, not substitutes for the definitions' complete text.

| Definition / source | Why it must be captured |
|---|---|
| street; street line; street setback line | Qualifying access, legal boundary and replacement measurement line; mapped and certain other streets differ |
| street, wide; street, narrow | 75-foot baseline plus express geographic/district exceptions |
| base plane; curb level | Elevation datum; building portions and frontage can require separate determinations |
| street wall; street wall line; street wall line level; rear wall line level | Distinguish building faces, projected lines and elevations |
| sky exposure plane or front sky exposure plane; sky exposure plane building | Plane geometry versus eligibility for the optional bulk route |
| zoning lot; lot area; lot width; lot depth; lot lines; block | Legal aggregation and dimensions; tax-lot identity alone is insufficient |
| lot, corner; lot, interior; lot, through; building segment | Frontage and portion-specific rules |
| prevailing street wall frontage; transportation infrastructure-adjacent frontage | Context and transportation conditions |
| qualifying affordable housing; qualifying senior housing | Select the correct height/FAR columns |
| [§66-11 Definitions](https://zr.planning.nyc.gov/article-vi/chapter-6/66-11) | Transit-specific sites, infrastructure and measurement terminology |
| [§27-111 General definitions](https://zr.planning.nyc.gov/article-ii/chapter-7/27-111) | Affordable-housing regulatory terms; distinct from geometry |

The wide-street definition specifically addresses certain C5-3/C6-4/C6-6 variable-width situations and named Broadway and Allen Street roadways separated by mapped park. The March 26, 2026 amendment date is visible in the retrieved definition. A numeric width comparison alone is an incomplete legal classification.

### Completeness boundary

This is the core Article II residential section map. A citywide envelope engine must also dispatch applicable [waterfront regulations, Article VI Chapter 2](https://zr.planning.nyc.gov/article-vi/chapter-2), [flood regulations, Chapter 4](https://zr.planning.nyc.gov/article-vi/chapter-4), [transit regulations, Chapter 6](https://zr.planning.nyc.gov/article-vi/chapter-6), [split-lot rules, Article VII Chapter 7](https://zr.planning.nyc.gov/article-vii/chapter-7), [large-scale residential development rules, Chapter 8](https://zr.planning.nyc.gov/article-vii/chapter-8), and the special chapters inventoried below. Site-specific approvals and recorded restrictions remain separate inputs. A chapter inventory is not proof that every parcel-specific override has been cleared.

## RQ-002: commercial FAR, overlays and residential equivalents

### The governing section structure

| Section and exact title | What the table or rule does |
|---|---|
| [33-12 Maximum Floor Area Ratio](https://zr.planning.nyc.gov/article-iii/chapter-3/33-12) | Parent FAR rule; multiple-use and bonus constraints, including district-specific exclusions |
| [33-121 In districts with bulk governed by Residence District bulk regulations](https://zr.planning.nyc.gov/article-iii/chapter-3/33-121) | C1-1 through C1-5 and C2-1 through C2-5 overlays; rows by underlying R district, columns for commercial-only, community-facility-only and combined uses |
| [33-122 Commercial buildings in all other Commercial Districts](https://zr.planning.nyc.gov/article-iii/chapter-3/33-122) | Two-column district-group/FAR table for standalone C1/C2 and C3-C8 |
| [33-123 Community facility buildings or buildings used for both community facility and commercial uses in all other Commercial Districts](https://zr.planning.nyc.gov/article-iii/chapter-3/33-123) | Separate community-facility/combined-use maxima, with commercial portion constrained by §33-122 |
| [34-111 Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District](https://zr.planning.nyc.gov/article-iii/chapter-4/34-111) | Residential buildings in overlays: underlying R rules, with explicit substitutions |
| [34-112 Residential bulk regulations in other C1 or C2 Districts or in C3, C4, C5 or C6 Districts](https://zr.planning.nyc.gov/article-iii/chapter-4/34-112) | Establishes the residential-equivalent mapping |
| [35-22 Residential Bulk Regulations in C1 or C2 Districts Whose Bulk Is Governed by Surrounding Residence District](https://zr.planning.nyc.gov/article-iii/chapter-5/35-22) | Corresponding overlay rule for residential portions of mixed buildings |
| [35-23 Residential Bulk Regulations in Other C1 or C2 Districts or in C3, C4, C5 or C6 Districts](https://zr.planning.nyc.gov/article-iii/chapter-5/35-23) | Imports §34-112 equivalents for mixed-building residential portions |
| [35-31 Maximum Floor Area Ratio](https://zr.planning.nyc.gov/article-iii/chapter-5/35-31) | Individual use caps plus the combined-building cap; do not simply add commercial FAR and residential FAR |
| [35-32 Maximum Floor Area for Mixed Buildings on Qualifying Residential Sites](https://zr.planning.nyc.gov/article-iii/chapter-5/35-32) | Express mixed-building alternative for qualifying sites; retains individual use caps |

The current §33-121 commercial-only column gives 1.0 for the R1/R2 and R3-1/R3A/R3X rows, 1.6 for R3-2, and 2.0 for R4/R5 rows. Do not carry forward the obsolete simplification that every low-density overlay has a 1.0 commercial cap. Its community-facility and combined-use columns are different quantities.

The standalone commercial table is not monotonic in the apparent district number. Under §33-122, C4-6 has commercial FAR 3.4, C4-7 has 10.0, C4-11/C4-12 have 3.4, C6-11 has 12.0 and C6-12 has 15.0. R11/R12 residential equivalency does not set the commercial FAR. Capture exact rows and exceptions.

### Overlay exceptions that change residential answers

§§34-111 and 35-22 ordinarily import the underlying residential rules. They also substitute R5 without a letter suffix for qualifying residential sites in the Greater Transit Zone mapped within R1-R5, and substitute R3-2 for non-qualifying sites mapped within R1/R2. These substitutions must be evaluated before selecting residential FAR or envelope rules. Quoting only the opening inheritance sentence would give an incomplete answer.

Under §35-32, qualifying mixed-building sites in the Greater Transit Zone can have a total FAR of 2.5, still subject to individual use caps. Outside that zone, its table has total caps of 1.5 for the specified R1/R2/R3-1/R3A/R3X group, 1.6 for R3-2, 2.0 for R4 and 2.5 for R5. Those combined caps do not independently authorize each use at that FAR.

### Residential equivalents: full mapping in §34-112

The research request's example is incorrect: **C4-6 corresponds to R10, not R7.** Preserve the distinctions between C4-4, C4-4A, C4-4D and other suffixes.

| Commercial designation(s) | Residential equivalent |
|---|---|
| C3 | R3-2 |
| C4-1 | R5 |
| C4-2, C4-3, C6-1A | R6 |
| C4-2A, C4-3A | R6A |
| C1-6, C2-6, C4-4, C4-5, C6-1 | R7-2 |
| C1-6A, C2-6A, C4-4A, C4-4L, C4-5A | R7A |
| C4-5D | R7D |
| C4-5X | R7X |
| C1-7, C4-2F, C4-8, C6-2 | R8 |
| C1-7A, C4-4D, C6-2A | R8A |
| C1-8, C2-7, C4-9, C6-3 | R9 |
| C1-8A, C2-7A, C6-3A | R9A |
| C6-3D | R9D |
| C1-8X, C2-7X, C6-3X | R9X |
| C1-9, C2-8, C4-6, C4-7, C5, C6-4, C6-5, C6-6, C6-7, C6-8, C6-9 | R10 |
| C1-9A, C2-8A, C4-6A, C4-7A, C5-1A, C5-2A, C6-4A | R10A |
| C6-4X | R10X |
| C4-11, C6-11 | R11 |
| C4-11A | R11A |
| C4-12, C6-12 | R12 |

The source's bare labels and explicit exceptions must remain attached to this mapping. C1/C2 overlays use the separate overlay provisions; there is no blanket C7/C8 residential-equivalent row here. [§32-121, Use Group II - general use allowances](https://zr.planning.nyc.gov/article-iii/chapter-2/32-121) marks ordinary residential uses as not permitted in C7/C8. Specific exceptions or special-district permissions require their own authority; equivalency is not a use-permission test. [§32-122, Use Group II - uses subject to limitations](https://zr.planning.nyc.gov/article-iii/chapter-2/32-122) further limits residential building types in C3A.

### Suffix rules

[§11-25, District Designations Appended with Suffixes](https://zr.planning.nyc.gov/article-i/chapter-1/11-25) is a general Resolution-wide construction rule. It is not restricted to residential districts. Its default inheritance is expressly subject to other express provisions. I found no separate universal commercial-suffix rule replacing it. The operational rule is to preserve the full designation, use the expressly named table row or exception when present, and apply general inheritance only where the text supports it. For example, contextual exceptions in §33-12 and explicit rows in §34-112 cannot be discarded by stripping the suffix.

## RQ-003: qualifying residential sites

### The full source was found

The current official [§12-10 definition](https://zr.planning.nyc.gov/article-i/chapter-2/12-10#term-qualifying%20residential%20site) includes all paragraphs (a)-(c) and the final affordability condition. Its displayed amendment date is December 5, 2024. The original, unmodified §12-10 HTML bytes are supplied in the evidence archive as `official/zr_12_10.html`. A readable `qualifying-residential-site.html` preserves the complete official definition fragment without rewriting its text. This preserves the complete text and nested lists for direct verification. The compact route index below is a discovery aid, not a verbatim replacement.

The website's whole-section print endpoint timed out during direct download. A search-accessible PDF response did not yield the searched term. I therefore do not claim to have completed print/PDF-class capture of this definition, and do not present that response as a verified complete substitute for the current HTML.

### Route index

All tests concern a zoning lot or its relevant portion. Alternatives are joined by OR; criteria within a route must all be met.

| Route | Locate and verify these conditions in the complete source |
|---|---|
| (a)(1) | R1-R5 framework; at least 5,000 square feet; Greater Transit Zone with restricted Outer Transit geography; wide-street or short-block frontage; excludes R1/R2 |
| (a)(2) | Greater Transit Zone plus qualifying community-facility floor space existing December 5, 2024 |
| (a)(3) | Outside that zone; at least 5,000 square feet; qualifying historical community-facility floor space |
| (a)(4) | Qualifying senior housing in the specified R3-2, bare R4, R5 or R5B districts |
| (b)(1) | Eligible C1/C2/C4: continuous commercial blockfront and adjacent-block mapping, plus the long-dimension residential-frontage test |
| (b)(2) | Commercial fallback to an (a) route, with an express qualification concerning residential-district limitations |
| (c) | M1 paired with R1-R5 |

The final paragraph adds affordability obligations when using §23-21's qualifying-site FAR and permitted residential floor area exceeds 50,000 square feet. It includes the FAR/1.2 threshold, weighted 80% income target, band limits, legal instrument and HPD requirements. Preserve that paragraph with the eligibility text.

### Cross-references and consequences

[§66-11, Definitions](https://zr.planning.nyc.gov/article-vi/chapter-6/66-11) supplies the mass-transit-station definition. Do not assume a station's map pin is the legally specified measurement origin. The Greater, Inner and Outer Transit Zone definitions in §12-10 and their map/text precedence provisions must also be captured. Route (a)(1)'s Outer Transit restriction refers to stations existing on December 5, 2024; an unrestricted current transit-zone polygon is not necessarily sufficient evidence for that route.

[§23-21, Floor Area Regulations for R1 Through R5 Districts](https://zr.planning.nyc.gov/article-ii/chapter-3/23-21) contains the qualifying-site FAR columns and is the final paragraph's express trigger. [§27-111, General definitions](https://zr.planning.nyc.gov/article-ii/chapter-7/27-111) supplies the affordability terms. [§23-424, Height and setback requirements for qualifying residential sites](https://zr.planning.nyc.gov/article-ii/chapter-3/23-424) supplies the alternative height table: 35/35 feet maximum base/building height for the named R1/R2/R3 districts, 35/45 for R4 and 45/55 for R5. Being a qualifying site does not erase other applicable provisions.

One concrete override surfaced during the special-district sweep: [§114-02, Applicability of Certain Provisions](https://zr.planning.nyc.gov/article-xi/chapter-4/114-02) excludes, within Special Bay Ridge, zoning lots existing on December 5, 2024 whose area exceeds five acres from the qualifying-site definition. That is an express counterexample to a citywide §12-10-only eligibility function.

The product should distinguish verified eligibility, verified ineligibility and unknown facts. Historical community-facility use, the commercial corridor frontage test, legal zoning-lot aggregation and affordability instruments are not established merely by a current tax-lot area and district code. That is an implementation recommendation, not a professional determination that a particular site qualifies.

## RQ-004: special-district inventory and priorities

### Inventory boundaries and source inconsistencies

The inventory below reconciles the current Articles VIII-XIV chapter pages with [§11-122, Districts established](https://zr.planning.nyc.gov/article-i/chapter-1/11-122) and DCP's [Special Purpose Districts guide](https://www.nyc.gov/content/planning/pages/zoning/zoning-districts-guide/special-purpose-districts). It contains 59 current chapter families, not 59 individual mapped polygons. Several families have multiple numbered districts or subdistricts.

Two front-matter inconsistencies require explicit handling. §11-122 still includes a Garment Center entry pointing to Article XII Chapter 1, while that chapter's current text is Special Midtown South Mixed Use. Article XIV Chapter 5 contains Special Eastchester-East Tremont Corridor, which was absent from the retrieved §11-122 list. Do not create two active Chapter 121 rule families or omit Chapter 145 merely by trusting that index.

The DCP explanatory guide is useful for geography but is not a current numeric rule source. For example, its Park Improvement summary says 210 feet/19 stories; current [§92-23](https://zr.planning.nyc.gov/article-ix/chapter-2/92-23) says 215 feet with qualifying-housing and obstruction provisions. Current section text takes priority in this research.

In the inventory, H means a residential height/setback, street-wall, obstruction or applicable bulk-route modification. F means a residential FAR amount, allocation, exemption or available FAR route is affected. “Conditional” includes discretionary changes or restrictions on an otherwise available route. “No direct” is a bounded finding about the chapter text, not a statement that the site has no other restrictions. Locations are orientation summaries; the mapped boundary and subdistrict govern a parcel.

| Article / chapter and district | Geography | Residential bulk effect; section targets |
|---|---|---|
| VIII/1 [Midtown District (MiD)](https://zr.planning.nyc.gov/article-viii/chapter-1) | Manhattan: Midtown, including East Midtown, Theater and Penn areas | H yes; F yes. §§81-241, 81-25, 81-26, 81-27 |
| VIII/2 [Lincoln Square District (L)](https://zr.planning.nyc.gov/article-viii/chapter-2) | Manhattan: Lincoln Square | H yes; F yes. §§82-31, 82-32 |
| VIII/3 [Limited Commercial District (LC)](https://zr.planning.nyc.gov/article-viii/chapter-3) | Manhattan: Greenwich Village historic commercial area | H no direct; F no direct (use/sign controls). §§83-02, 83-10 |
| VIII/4 [Battery Park City District (BPC)](https://zr.planning.nyc.gov/article-viii/chapter-4) | Manhattan: Battery Park City | H yes; F yes. §§84-13, 84-33 |
| VIII/5 [United Nations Development District (U)](https://zr.planning.nyc.gov/article-viii/chapter-5) | Manhattan: UN vicinity, East 43rd-45th Streets | H yes; F conditional allocation, underlying residential cap. §§85-04, 85-05 |
| VIII/6 [Forest Hills District (FH)](https://zr.planning.nyc.gov/article-viii/chapter-6) | Queens: Forest Hills commercial center | H yes; F commercial change only in 86-21. §§86-21, 86-23 |
| VIII/7 [Harlem River Waterfront District (HRW)](https://zr.planning.nyc.gov/article-viii/chapter-7) | Bronx: Harlem River waterfront / Lower Concourse | H yes; F yes. §§87-20, 87-30 |
| VIII/8 [Hudson Square District (HSQ)](https://zr.planning.nyc.gov/article-viii/chapter-8) | Manhattan: Hudson Square | H yes; F yes. §§88-31, 88-33 |
| VIII/9 [Hudson River Park District (HRP)](https://zr.planning.nyc.gov/article-viii/chapter-9) | Manhattan: Hudson River Park and mapped receiving sites | H conditional; F transfer and use/bulk substitutions. §§89-11, 89-21 |
| IX/1 [Lower Manhattan District (LM)](https://zr.planning.nyc.gov/article-ix/chapter-1) | Manhattan: Lower Manhattan, including Seaport | H yes; F yes. §§91-21, 91-30, 91-66 |
| IX/2 [Park Improvement District (PI)](https://zr.planning.nyc.gov/article-ix/chapter-2) | Manhattan: Fifth/Park Avenue corridors, East 59th-111th | H yes; F bonus restrictions/exceptions. §§92-21, 92-23 |
| IX/3 [Hudson Yards District (HY)](https://zr.planning.nyc.gov/article-ix/chapter-3) | Manhattan: Hudson Yards / Far West Side | H yes; F yes. §§93-20, 93-40, 93-50 |
| IX/4 [Sheepshead Bay District (SB)](https://zr.planning.nyc.gov/article-ix/chapter-4) | Brooklyn: Sheepshead Bay waterfront center | H yes; F yes. §§94-09, 94-10 |
| IX/5 [Transit Land Use District (TA)](https://zr.planning.nyc.gov/article-ix/chapter-5) | Manhattan: Second Avenue subway corridor sites | H no direct general cap; F easement exemption/conditional bonus. §§95-03, 95-05 |
| IX/6 [Clinton District (CL)](https://zr.planning.nyc.gov/article-ix/chapter-6) | Manhattan: Clinton / Hell's Kitchen | H yes; F yes. §§96-101, 96-103, 96-23 |
| IX/7 [125th Street District (125)](https://zr.planning.nyc.gov/article-ix/chapter-7) | Manhattan: 125th Street corridor | H yes; F yes. §§97-41, 97-43 |
| IX/8 [West Chelsea District (WCh)](https://zr.planning.nyc.gov/article-ix/chapter-8) | Manhattan: West Chelsea / High Line | H yes; F yes. §§98-20, 98-42, 98-50 |
| IX/9 [Madison Avenue Preservation District (MP)](https://zr.planning.nyc.gov/article-ix/chapter-9) | Manhattan: Madison Avenue preservation corridor | H yes; F yes. §§99-21, 99-22 |
| X/1 [Downtown Brooklyn District (DB)](https://zr.planning.nyc.gov/article-x/chapter-1) | Brooklyn: Downtown Brooklyn, Fulton/Atlantic subareas | H yes; F yes. §§101-21, 101-22, 101-72 |
| X/2 [Scenic View District (SV-1)](https://zr.planning.nyc.gov/article-x/chapter-2) | Brooklyn: Brooklyn Heights scenic-view area | H yes, view plane; F no direct. §§102-10, 102-61 |
| X/3 [Planned Community Preservation District (PC)](https://zr.planning.nyc.gov/article-x/chapter-3) | Bronx: Parkchester; Queens: Sunnyside Gardens/Fresh Meadows; Manhattan: Harlem River Houses | H conditional; F conditional allocation. §§103-10, 103-11 |
| X/4 [Manhattanville Mixed Use District (MMU)](https://zr.planning.nyc.gov/article-x/chapter-4) | Manhattan: Manhattanville / West Harlem campus area | H yes; F yes, uses differ. §§104-21, 104-30, 104-50 |
| X/5 [Natural Area District (NA)](https://zr.planning.nyc.gov/article-x/chapter-5) | Staten Island: central hills/wetlands, Shore Acres; Bronx: Riverdale/Fieldston/Spuyten Duyvil; Queens: Fort Totten | H conditional natural-feature review; F conditional large-scale route. §§105-432, 105-70 |
| X/6 [Coney Island Mixed Use District (CO)](https://zr.planning.nyc.gov/article-x/chapter-6) | Brooklyn: Coney Island mixed-use area, distinct from Ch. 131 | H/F no direct replacement found; residential use and yard gates. §§106-11, 106-12, 106-40 |
| X/7 [South Richmond Development District (SRD)](https://zr.planning.nyc.gov/article-x/chapter-7) | Staten Island: South Richmond / South Shore | H yes; F lot-area/open-space and special-area mechanics. §§107-224, 107-225, 107-43, 107-67 |
| X/8 [Hunts Point District (HP)](https://zr.planning.nyc.gov/article-x/chapter-8) | Bronx: Hunts Point | H/F no direct replacement found; manufacturing/use/buffer rules. §§108-10, 108-20 |
| X/9 [Little Italy District (LI)](https://zr.planning.nyc.gov/article-x/chapter-9) | Manhattan: Little Italy / Nolita | H yes; F yes. §§109-12, 109-22, 109-32, 109-41 |
| XI/1 [Tribeca Mixed Use District (TMU)](https://zr.planning.nyc.gov/article-xi/chapter-1) | Manhattan: Tribeca | H yes; F yes, area-specific. §§111-20 |
| XI/2 [City Island District (CD)](https://zr.planning.nyc.gov/article-xi/chapter-2) | Bronx: City Island | H yes; F no direct general residential cap. §§112-11, 112-12, 112-13 |
| XI/3 [Ocean Parkway District (OP)](https://zr.planning.nyc.gov/article-xi/chapter-3) | Brooklyn: Ocean Parkway corridor and mapped subdistrict | H yes; F yes, subdistrict. §§113-13, 113-521, 113-523 |
| XI/4 [Bay Ridge District (BR)](https://zr.planning.nyc.gov/article-xi/chapter-4) | Brooklyn: Bay Ridge | H obstruction modification; F eligibility/use-specific effects. §§114-02, 114-11, 114-121, 114-122 |
| XI/5 [Downtown Jamaica District (DJ)](https://zr.planning.nyc.gov/article-xi/chapter-5) | Queens: Downtown Jamaica | H yes; F conditional bonus/exemption and route limits. §§115-21, 115-23 |
| XI/6 [Stapleton Waterfront District (SW)](https://zr.planning.nyc.gov/article-xi/chapter-6) | Staten Island: Stapleton waterfront | H yes; F yes. §§116-22, 116-23, 116-62 |
| XI/7 [Long Island City Mixed Use District (LIC)](https://zr.planning.nyc.gov/article-xi/chapter-7) | Queens: Long Island City, Hunters Point, Queens Plaza, Court Square, Dutch Kills | H yes; F yes, subdistrict-specific. §§117-22, 117-24, 117-42, 117-52, 117-63 |
| XI/8 [Union Square District (US)](https://zr.planning.nyc.gov/article-xi/chapter-8) | Manhattan: Union Square | H yes; F yes. §§118-21, 118-22 |
| XI/9 [Hillsides Preservation District (HS)](https://zr.planning.nyc.gov/article-xi/chapter-9) | Staten Island: mapped hillside areas | H yes; F private-road lot-area effect. §§119-211, 119-212, 119-315 |
| XII/1 [Midtown South Mixed Use District (MSX)](https://zr.planning.nyc.gov/article-xii/chapter-1) | Manhattan: Midtown South | H yes; F exemption/transfer mechanisms; paired-district framework. §§121-31, 121-33, 121-34 |
| XII/2 [Grand Concourse Preservation District (C)](https://zr.planning.nyc.gov/article-xii/chapter-2) | Bronx: Grand Concourse corridor | H yes; F residential R8X substitution. §§122-30 |
| XII/3 [Mixed Use District (MX)](https://zr.planning.nyc.gov/article-xii/chapter-3) | Bronx, Brooklyn, Manhattan, Queens: multiple MX areas; see 123-90 | H yes; F yes; retain each MX number. §§123-62, 123-64, 123-65, 123-90 |
| XII/4 [Willets Point District (WP)](https://zr.planning.nyc.gov/article-xii/chapter-4) | Queens: Willets Point | H yes; F yes. §§124-21, 124-22 |
| XII/5 [Southern Hunters Point District (SHP)](https://zr.planning.nyc.gov/article-xii/chapter-5) | Queens: Southern Hunters Point waterfront | H yes; F yes. §§125-20, 125-30 |
| XII/6 [College Point District (CP)](https://zr.planning.nyc.gov/article-xii/chapter-6) | Queens: College Point industrial area | Ordinary residential lane not established; special nonresidential H/F. §§126-10, 126-22, 126-24 |
| XII/7 [Flushing Waterfront District (FW)](https://zr.planning.nyc.gov/article-xii/chapter-7) | Queens: Flushing waterfront | H yes; F yes. §§127-21, 127-23 |
| XII/8 [St. George District (SG)](https://zr.planning.nyc.gov/article-xii/chapter-8) | Staten Island: St. George / north waterfront | H yes; F yes. §§128-21, 128-30, 128-52 |
| XIII/1 [Coney Island District  (CI)](https://zr.planning.nyc.gov/article-xiii/chapter-1) | Brooklyn: Coney Island amusement and adjacent residential areas | H yes; F yes, residential subareas. §§131-321, 131-40 |
| XIII/2 [Enhanced Commercial District (EC)](https://zr.planning.nyc.gov/article-xiii/chapter-2) | Manhattan: Upper West Side avenues; Brooklyn: Fourth Avenue, Broadway and East New York corridors | H/F no direct replacement; ground-floor use/frontage controls. §§132-11, 132-20 |
| XIII/3 [Southern Roosevelt Island District (SRI)](https://zr.planning.nyc.gov/article-xiii/chapter-3) | Manhattan: southern Roosevelt Island | H yes; F underlying with optional-route restriction. §§133-21, 133-23 |
| XIII/4 [Governors Island District (GI)](https://zr.planning.nyc.gov/article-xiii/chapter-4) | Manhattan: Governors Island | Use-limited development; special H/F applies to permitted program, not a generic housing entitlement. §§134-11, 134-21, 134-24 |
| XIII/5 [Bay Street Corridor District (BSC)](https://zr.planning.nyc.gov/article-xiii/chapter-5) | Staten Island: Bay Street corridor | H yes; F yes. §§135-21, 135-23 |
| XIII/6 [Downtown Far Rockaway District (DFR)](https://zr.planning.nyc.gov/article-xiii/chapter-6) | Queens: Downtown Far Rockaway | H yes; F no direct replacement numeric residential cap identified. §§136-20, 136-22, 136-23, 136-31 |
| XIII/7 [Coastal Risk District (CR)](https://zr.planning.nyc.gov/article-xiii/chapter-7) | Queens: Broad Channel/Hamilton Beach/Edgemere; Staten Island: buyout areas; Brooklyn: Gerritsen Beach | H yes in CR-4; F no direct general replacement; use/density gates remain. §§137-11, 137-12, 137-21, 137-32 |
| XIII/8 [East Harlem Corridors District (EHC)](https://zr.planning.nyc.gov/article-xiii/chapter-8) | Manhattan: East Harlem corridors / Park Avenue subdistrict | H yes; F yes. §§138-211, 138-23, 138-24 |
| XIII/9 [Gowanus Mixed Use District (G)](https://zr.planning.nyc.gov/article-xiii/chapter-9) | Brooklyn: Gowanus | H yes; F yes. §§139-211, 139-23 |
| XIV/1 [Jerome Corridor District  (J)](https://zr.planning.nyc.gov/article-xiv/chapter-1) | Bronx: Jerome Avenue corridor | H yes; F yes in specified districts. §§141-22, 141-23, 141-24, 141-25 |
| XIV/2 [Inwood District (IN)](https://zr.planning.nyc.gov/article-xiv/chapter-2) | Manhattan: Inwood | H yes; F yes in specified subareas. §§142-22, 142-40 |
| XIV/3 [SoHo-NoHo Mixed Use District (SNX)](https://zr.planning.nyc.gov/article-xiv/chapter-3) | Manhattan: SoHo and NoHo | H yes; F yes. §§143-21, 143-23 |
| XIV/4 [Brooklyn Navy Yard District (BNY)](https://zr.planning.nyc.gov/article-xiv/chapter-4) | Brooklyn: Navy Yard | Manufacturing framework; nonresidential H/F modifications, no generic housing entitlement. §§144-10, 144-20 |
| XIV/5 [Eastchester – East Tremont Corridor District (ETC)](https://zr.planning.nyc.gov/article-xiv/chapter-5) | Bronx: Eastchester/East Tremont corridors, station areas | H yes; F yes. §§145-21, 145-23 |
| XIV/6 [Atlantic Avenue Mixed Use District (AAM)](https://zr.planning.nyc.gov/article-xiv/chapter-6) | Brooklyn: Atlantic Avenue mixed-use corridor | H yes; F yes. §§146-21, 146-23 |


Limited Height Districts LH-1, LH-1A, LH-2 and LH-3 also need dispatch under §§23-443(c) and 23-739. They are separate from these special-purpose chapter families. Scenic View, Natural Area, Coastal Risk, Enhanced Commercial and Mixed Use families also require their numbered designations to be preserved.

### A measured activity ranking, with its limitations

I calculated the following ranking from DCP's [Housing Database Project Level Files, version 25Q4](https://data.cityofnewyork.us/Housing-Development/Housing-Database-Project-Level-Files/br6q-ssj3) and the official [NYSP Special Purpose District boundaries](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nysp/FeatureServer/0). The metric is the sum of positive net proposed Class A units in unique, non-withdrawn jobs permitted from 2021 through 2025, whose supplied point falls in the retrieved district boundary. It includes new-building and alteration jobs. It is not completed housing, total construction spending, net citywide housing growth, or an assessment of future rezoning capacity.

The input returned 9,002 unique jobs, all marked 25Q4. Fifty withdrawn jobs were excluded. The spatial join placed 1,448 remaining jobs in at least one special district; 7,504 were outside the retrieved special boundaries. Polygons were last edited August 17, 2026. Thus this is historical permit activity grouped by the retrieved 2026 geography, not a reconstruction of the legal district at the permit date.

| Rank by units | Special-district family | Positive net proposed Class A units | Jobs |
|---|---|---:|---:|
| 1 | Gowanus | 8,660 | 49 |
| 2 | Mixed Use (all mapped MX districts combined) | 8,609 | 122 |
| 3 | Lower Manhattan | 7,337 | 22 |
| 4 | Long Island City Mixed Use | 6,645 | 64 |
| 5 | Downtown Brooklyn | 6,227 | 31 |
| 6 | Downtown Jamaica | 5,014 | 45 |
| 7 | Midtown | 3,723 | 21 |
| 8 | Enhanced Commercial (all EC districts combined) | 2,737 | 36 |
| 9 | Jerome Corridor | 2,222 | 15 |
| 10 | Transit Land Use | 2,089 | 12 |

This uses project coordinates instead of the applicant-entered special-district fields, which DCP's dictionary explicitly describes as inconsistent and potentially containing other zoning designations. Five input polygons were invalid and processed with GEOS/Shapely make_valid before the join. Seven project memberships changed in Downtown Jamaica; direct point queries to DCP's service confirmed all seven resulting exclusions. All input geometries, the script, matched-job audit, verification responses and full ranking are supplied for reproduction. There were no points exactly on a resulting boundary. Point assignment still cannot resolve a split zoning lot or prove parcel-specific applicability. Jobs can belong to overlapping special families; each is counted once within a family, so the table is not additive. Withdrawn jobs and negative-unit jobs are excluded, and proposed units may never be built.

The question's examples do not all rank near the top under this metric: Ocean Parkway has 1,181 units in 139 jobs (19th by units); Hudson Yards 1,015 in nine jobs (21st); Hillsides Preservation 175 in 65 jobs (27th). South Richmond has 940 units in 548 jobs, the highest job count among special families. Those facts support a separate small-house priority lane rather than treating unit volume as the only product value measure.

### Suggested implementation order

For residential height/FAR coverage, prioritize Gowanus, Mixed Use, Lower Manhattan, Long Island City, Downtown Brooklyn, Downtown Jamaica, Midtown and Jerome Corridor, then Harlem River Waterfront and Inwood (the latter two have 2,007 and 1,904 units in this analysis). This is my planning recommendation, not another measured top-ten claim. Enhanced Commercial and Transit Land Use rank highly by geographic activity but do not require the same scale of residential height/FAR replacement; targeted handling of their actual controls can be a separate task.

For small-house deal coverage, put South Richmond, Ocean Parkway, Hillsides Preservation and Natural Area rules on a separate priority track. For future opportunities, independently track Midtown South, Atlantic Avenue and Eastchester-East Tremont. Recent special-district creation and the historical data window make low historical counts an unsuitable measure of their future capacity. No forecast of new housing production is implied here.


## RQ-005: DCM and LION width provenance

### 1. DCM: mapped width is supported; the exact field convention remains open

DCP's [Street Center Line metadata](https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/dcm_street_centerline.pdf), page 1, describes the dataset as representing official street names and widths from the Official City Map. Its source description includes paper streets and map records; record and unmapped streets are included for context. This supports identifying DCM's intended width concept as mapped width.

The official Street Map application's [published explanatory text](https://streets.planning.nyc.gov/assets/city-map-57ba917a8f2d723f4657d3430e37df3d.js) also states: “Some streets are built narrower than their mapped width, with unimproved areas on the sides.” I recovered this text from the city's publicly served application file after the page failed to render. It supports the mapped-versus-built distinction but does not supply the missing field-level measurement convention.

But page 4 gives the `Streetwidt` field a string type and width 50, without a field description. I checked the metadata XML actually inside the downloaded shapefile ZIP, too: its `Streetwidt` attribute likewise has no `attrdef`. Thus the original gap is real, not just a PDF text-extraction failure. “Width 50” is the string field capacity, not 50 feet of street.

I did not recover an authoritative field specification explicitly defining its geometric measurement as property-line-to-property-line, its treatment of variable widths, or how every nonnumeric value is encoded. It would be dishonest to mark that precise question closed. The dataset-level mapped-width description is evidence; equating every field value to a complete zoning width determination would add an inference.

[§12-10's street and street-line definitions](https://zr.planning.nyc.gov/article-i/chapter-2/12-10) identify the legal concepts. A street setback line can supersede a street line for certain bulk measurements. Neither a tax-parcel gap measurement nor LION's pavement measurement is an automatic replacement for those concepts. The remaining verification target is DCP Technical Review / the relevant Borough Topographical Office's field convention and the applicable City Map or alteration for ambiguous segments. This report does not assign an ambiguity policy on the owner's behalf.

### 2. Exact bulk-product download: verified against the bytes

The rendered [DCP Digital City Map download page](https://www.nyc.gov/content/planning/pages/resources/datasets/digital-city-map) lists the latest release as October 2025, with data dated October 31, 2025. Its stated monthly frequency should not be mistaken for evidence that a newer release was retrieved.

| Fact | Verified value |
|---|---|
| Official download filename | dcm_20251031shp.zip |
| Internal street-centerline shapefile | DCM_StreetCenterLine.shp |
| Attribute table | DCM_StreetCenterLine.dbf |
| Embedded metadata | DCM_StreetCenterLine.shp.xml |
| Shapefile width field | Streetwidt (10-character name), string capacity 50 |
| ZIP byte count | 19,554,628 |
| ZIP SHA-256 | ad21afd2c7c6c2b18dfa76b2776ef896562246437069d52bb4ec5600e575f527 |

Exact downloadURL: [dcm_20251031shp.zip](https://s-media.nyc.gov/agencies/dcp/assets/files/zip/data-tools/bytes/digital-city-map/dcm_20251031shp.zip). This is the full DCM product ZIP, containing multiple layers; it is not a separate ZIP named only for street centerlines. The URL came from DCP's rendered page and returned an actual ZIP that I opened. A file geodatabase option exists alongside it and is a different product.

The service is separately published as [DCM Street Center Line, FeatureServer layer 0](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/DCM_Street_Center_Line/FeatureServer/0). Preserve the field name and schema from the chosen product rather than assuming service and shapefile field names are identical. Preserve source status attributes, including record/paper/unmapped indications, with any parsed width.

### 3. LION: the PDF was downloaded, OCR-read and visually checked

The [current original LION metadata PDF](https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/lion_metadata.pdf) identifies Release 26C. Page 24 names `StreetWidth_Min`, with alias `StreetWidth`, type Double. The decisive exact excerpt is:

> “Formerly known as StreetWidth, this represents the narrowest width, in feet, of the paved area of the street.”

The field description then associates these values with Geosupport's StreetWidth field. Page 30 defines `StreetWidth_Max` in terms of the maximum paved width. Page 24 also says the consistency flag `StreetWidth_Irr` is not currently implemented. The complete original field-description page is in the supplied original `lion_26c.pdf`; these findings are based on the actual PDF image, not a search snippet.

The current PDF is 1,389,272 bytes, SHA-256 b98255a244046fc8b779652df2a36266fde71e133f9021ced03f809b92017ef4. An older NYC assets URL encountered during research returned a Release 22B document; it should not be silently substituted for the current source.

This closes the pavement-versus-mapped distinction for LION. It does not close DCM's missing field convention, nor authorize treating a pavement value of 75 feet as the sole legal wide-street test.

## Related earlier question: §23-421(g)

I also directly retrieved the previously unverified paragraph in [§23-421, Basic pitched-roof envelopes for certain districts](https://zr.planning.nyc.gov/article-ii/chapter-3/23-421). Paragraph (g) applies in R1/R2 districts without a letter suffix. Its lot test is either: area at least 9,500 square feet AND width at least 100 feet; OR slope at least five percent, measured from street wall line level to rear wall line level. Where applicable, the reference plane may be up to five feet above the base plane.

Thus the 9,500-square-foot and 100-foot tests are joined by AND; the slope test is an alternative. The letter exclusion is explicit in (g), so that paragraph is not authority for an R1-2A, R2A or R2X five-foot adjustment. Numeric suffixes alone are not letter suffixes. This adjusts the reference plane for the section's envelope mechanics; it should not be encoded as an unconditional extra five feet for every R1/R2-family lot. The general suffix rule in §11-25 and the applicability of other height provisions remain separate questions. The original §23-421 HTML is included in the source archive.

## Handoff and remaining decisions

The strongest immediate factual corrections are: use R10 for C4-6; preserve overlay substitutions; keep standard and optional sky-plane routes separate; capture the complete qualifying-site definition and special exceptions; use the verified DCM ZIP/internal filenames; and stop treating LION StreetWidth as mapped street width.

The accompanying source archive contains the requested queue snapshot, original official HTML and metadata, the complete original LION PDF, the DCM metadata XML, source URL/hash manifests and the activity analysis inputs/results. The research report is a discovery aid. The build should cite its own verified official captures for rule provenance. Any choice about applying ambiguous text, accepting incomplete historical evidence or resolving width ambiguity remains an owner/professional decision under the project's stated process.

No conclusion here certifies an individual lot's buildability. The concrete unresolved factual item is the exact DCM field convention; print/PDF-class capture of the qualifying-site definition was not completed. The special-district index discrepancies and the optional-route/Limited-Height cross-reference should be expressly reviewed when those families are encoded.
