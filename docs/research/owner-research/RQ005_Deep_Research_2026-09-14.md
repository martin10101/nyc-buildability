> [Receiving-session note, 2026-09-13/14, D-050-R002: owner-returned deep-research result
> (third RQ-005 pass, research date 2026-09-14), received via the D-050 channel and archived
> verbatim below as a DISCOVERY AID. It is NOT provenance: every load-bearing claim must be
> captured from the official source under the normal discipline before encoding. Its evidence
> package stays with the owner (thin client). Queue stamps: docs/RESEARCH_REQUESTS.md RQ-005.]

# RQ-005: What NYC's mapped street-width data means

## Findings

**The DCM street-width field is best understood as a text description of mapped street width. Public evidence does not establish a universal rule that every value is a minimum, maximum, average, or measurement at a particular point.** This conclusion is supported by DCP's dataset description, current ingestion configuration, original developer discussion, and actual centerline records.[^1][^2][^3]

The deeper evidence answers more than a bare “the documentation is missing.” DCP's developers deliberately handled qualified width labels in 2018. Four adjoining East 96th Street features demonstrate that some width transitions are represented by successive numeric and range labels. Publicly accessible Section Maps and Alteration Maps provide a way to investigate a particular frontage without first obtaining a universal data dictionary.[^3][^4][^5]

| Question | Answer supported by the evidence | Remaining limit |
|---|---|---|
| What kind of width is represented? | Width shown on the Official City Map; the Street Map description says mapped widths usually include sidewalks. | This is a dataset description, not certification of every record's geometry or accuracy. |
| Are ranges and qualified values intentional? | Yes. Publisher discussion and live records establish that these are retained source annotations. | Their complete encoding rules, tolerances and spatial coverage are not documented in the located sources. |
| Can an individual frontage be resolved now? | Often, by reading the applicable, effective map dimensions and applying the relevant zoning provision. | Irregular geometry, unclear annotations or uncertain amendment effectiveness can still prevent a defensible answer. |
| Can RQ-005(1) be closed as a universal automated interpretation? | Not on this evidence alone. | A publisher specification or an explicitly approved policy is still needed for the unresolved generalizations. |

These are research findings, not a qualified professional's approval of product rules. Any new interpretation adopted for the product remains subject to its owner-decision and DRAFT review process. The research does not itself authorize a change in legal classification or rule coverage.[^6]

<!-- pagebreak -->

## 1. What the publisher actually says and preserves

DCP's ingestion template describes the product as representing official street names and widths shown on the Official City Map. It declares `streetwidt` as text. The listed transformations address names, date fields and geometry; none defines a width statistic. This is evidence about the published pipeline, not proof that no additional convention exists in the upstream mapping office.[^1]

The public Street Map description calls the values mapped street widths and says they usually include sidewalks. Its source configuration displays the width with feet. The ArcGIS service likewise declares `Streetwidth` as a nullable string rather than a numeric measurement with an accompanying min/max domain.[^2][^7][^8]

The strongest new evidence is DCP's April 18, 2018 pull request, **“prevent streetwidth SQL and template from showing na ft.”** The author distinguishes nulls from the literal text `Unknown`, observes that unknowns can be combined with measurements, and changes label construction. The included screenshot reads `Unknown but <71.2 ft` on Wall Street. The discussion directly establishes that qualified annotations were part of the publisher's intended display, rather than a downstream parser inventing them. It does not define a tolerance or guarantee that a bound applies everywhere along a feature.[^3]

![DCP's 2018 screenshot of the qualified Wall Street width label.](https://user-images.githubusercontent.com/409279/38954692-589a6546-4320-11e8-82b6-26e477494320.png)

The 2019 migration instructions identify `Streetwidth` as an extracted field in the TRD source feature class. They describe how to carry it into the download and application, without supplying an entry manual. A separate width-change visualization ticket has no substantive explanation of a measurement algorithm in its public discussion. Ticket closure alone cannot establish what algorithm was implemented.[^9][^10]

**Analytical consequence:** preserve the label as a source assertion. Converting all values to a single number would discard information the publisher intentionally retained. A parser may recognize a range or inequality, but recognition is different from establishing the assertion's geographical extent or legal sufficiency.

ZoLa and Street Map agreement is also weaker corroboration than it first appears. DCP's ZoLa discussion says its street-width labels were to use those from Street Map. The two interfaces therefore do not constitute two independent width determinations.[^11]

<!-- pagebreak -->

## 2. The relevant boundaries are mapped street boundaries

NYC Administrative Code §25-101 makes the City Map conclusive concerning street location, width and grades insofar as they have been duly adopted. It establishes the controlling map record, rather than a formula for interpreting the separate DCM text field. A historical map, a current display label and a duly effective alteration are different pieces of evidence.[^12]

“Building line to building line” is not a sufficiently precise general description. A building can be set back from the mapped street boundary. Current pavement edges and current tax-parcel lines can also differ from the legally mapped street. The sounder description is **width between the relevant mapped street boundaries**, with the applicable legal street and any special provisions established separately.

An official BSA decision provides a concrete example. **BSA 4-07-A, adopted April 1, 2008**, concerns premises on Tiemann Avenue in the Bronx. It records Tiemann Avenue's Final Map width as **60 feet, property line to property line**. This is direct evidence of how the width was described for that case; it does not establish today's width at every Tiemann frontage or the meaning of every DCM field. The decision's separate sidewalk discussion contains an apparent street-name inconsistency, so those pavement numbers are not used here.[^13]

A second, independently inspectable record is Bronx **Plan 11474, dated April 18, 1956**, available as `cp12444.pdf` through the city's map collection. It concerns grade changes and depicts Tiemann Avenue between Givan and Tillotson Avenues with a 60-foot dimension across the outer street lines. A sampled DCM feature on this portion, service OBJECTID 1691, also carries `60`. Agreement supports this particular map-reading example; the grade map alone is not an exhaustive search of later changes.[^14][^8]

| Source or geometry | What it establishes | What it does not establish |
|---|---|---|
| Duly adopted and effective City Map | The controlling mapped location and width | How every DCM label was compiled |
| DCM centerline and width text | A published map-derived annotation attached to a feature | A survey or guaranteed width at every adjoining frontage |
| Pavement or curb geometry | Physical roadbed configuration | The full legal mapped width |
| Tax-lot polygon | A parcel representation for the dataset's purposes | The whole zoning lot or necessarily the mapped street boundary |

Geosupport offers a useful comparison: its dictionary explicitly defines paved-width minimum and maximum fields. Those are documented conventions for Geosupport's paved area. Their existence does not transfer that meaning to a differently sourced DCM field.[^15]

<!-- pagebreak -->

## 3. Actual variable-width records provide a partial answer

Four adjoining DCM features on East 96th Street in Brooklyn form the sequence below. The annotations and geometry were checked in the October 31, 2025 shapefile release and in the public service retrieved September 14, 2026. Consecutive geometries share endpoints; the distances between them are zero in the source coordinate system.[^4][^8]

| Service OBJECTID | Exact width text | Centerline segment length, feet |
|---|---|---|
| 42351 | `60` | 249.43 |
| 183 | `60-75` | 27.21 |
| 15472 | `75-90` | 27.20 |
| 14008 | `90` | 57.50 |

The last column measures each centerline's length, **not street width**. It is included to show that the two range annotations belong to short transition features. Lengths were computed in EPSG:2263, whose units are US survey feet, and agree with the service's reported geometry lengths. Object identifiers refer to the captured service state and are not assumed stable across future publications.

This example establishes three limited but useful facts. A street name can have multiple width annotations. A variation can be represented by splitting the centerline. A range can be retained as text on the resulting short feature. Consequently, assigning a single width to a whole named street, or selecting one nearby segment without examining frontage coverage, can erase relevant information.

The example **does not establish** that the two endpoints of every range are measured at the two endpoints of its centerline. It does not prove a linear taper, a measurement perpendicular to the centerline, a citywide minimum/maximum rule, or the absence of smaller variations inside a feature. Those would be additional inferences beyond the observed data.

The corresponding public Section Map, **Brooklyn Final Section Map 58**, was successfully retrieved. It supplies mapping context for the East 96th Street transition near the rail corridor. Merely retrieving that sheet does not certify a numerical width for an unspecified lot or complete the search for effective alterations.[^5]

The full release contains **54,051 centerline records**. A profile classified 47,143 labels as plain numeric and 6,908 as other text forms, approximately 12.8%. This is a formatting count, not an accuracy test or a count of unusable streets. Non-numeric entries include informative bounds as well as unknowns. Conversely, numeric formatting does not establish correct frontage assignment.[^4]

The reproducible evidence package includes the original release, the four live feature records, and a CSV/JSON table of this sequence. Other nearby lines are excluded from the contiguous sequence when their geometry does not touch. This prevents apparent ordering in a table from being mistaken for spatial continuity.

<!-- pagebreak -->

## 4. What unusual values can and cannot tell an application

The table below separates literal recognition of an annotation from validation of its use. These are proposed data-handling distinctions, not a newly discovered DCP encoding specification. Except for the historical Wall Street screenshot identified separately, the examples occur in the captured DCM release.[^3][^4]

| Source text | Information worth preserving | Unproven step that must not be hidden |
|---|---|---|
| `60` | A reported numeric mapped width, in the display's feet convention | Assuming it is a certified minimum or applies to the entire selected frontage |
| `60-75` | A reported range with two numbers | Replacing it with 60, 67.5 or 75; assuming endpoint locations or interpolation |
| `>75` | A strict greater-than assertion | Treating its spatial coverage and source accuracy as already verified |
| `Unknown but >75` | Unknown exact value plus a stated lower bound | Discarding either the uncertainty or the bound |
| `~75` | An approximate value near 75 | Inventing a tolerance or choosing a threshold side |
| `Probably between 80 - 90` | A qualified range | Treating probability wording as an unconditional guarantee |
| `Width Irregular` | An irregularity warning without a usable number | Selecting a number from unrelated nearby segments |
| `n/a`, `Unknown`, or null | The original missing/unknown form | Claiming all three have an officially specified, identical meaning |

An inequality has ordinary mathematical meaning. If a trustworthy assertion of greater than 75 feet is shown to cover the entire relevant frontage, it can establish a threshold relation without an exact number. The unsettled step is whether this particular source annotation supplies that trustworthy, frontage-wide assertion. The proposed application must make that step explicit.

For a range touching or crossing 75 feet, the treatment depends on which street portion and zoning provision matter. A label such as `60-75` is not enough to choose a citywide narrow/wide classification rule. A label such as `~75` cannot be resolved by rounding because the approximation's tolerance is unspecified.

At minimum, a DRAFT implementation should retain the original text, the recognized form, any numbers and qualifiers, the source version, the matched geometry and the reason a frontage is considered covered. A separately recorded legal classification should identify the provision applied. This permits later professional review without losing the original evidence.

Such representation can be developed before every legal question is resolved. Activating a proposed inference for product outputs is a separate owner/professional decision. Nor should unknown width be treated as universally “safe if narrow”: the effect of a fallback depends on the consuming rule. The current research queue already recognizes that distinction, so this report does not present it as an uncorrected implementation defect.[^6]

<!-- pagebreak -->

## 5. A 2026 case separates measured width from zoning classification

The Allen Street Mall application is unusually useful because it documents the distinction in a current official proceeding. The CPC's **C 250306 MMM report, February 18, 2026**, describes Allen Street between Delancey and Rivington Streets as mapped at **138 feet**, despite a tax lot for the central mall. Mapping the center as parkland would leave two approximately **56-foot streets**. The report says no physical lane reconfiguration is proposed and identifies a related zoning text change needed to preserve existing treatment.[^16]

Two statuses must be kept separate. The mapping report conditions effectiveness on the required filing of certified counterparts; effectiveness is the following day. Proof that those filings occurred was not established here. Separately, the current ZR §12-10 wide-street definition, last amended **March 26, 2026**, does contain the Allen Street exception. The current zoning text is therefore verified independently of the map amendment's effective date.[^16][^17]

The paired text application, **N 250307 ZRM**, explains the purpose of preserving wide-street treatment after the mall becomes mapped parkland. This demonstrates that the legal classification can be maintained through an express provision even when the mapped configuration would otherwise produce roadways below the ordinary width threshold.[^18]

Sampled Allen Street centerline records in both the October 2025 download and the live service still report `138`. That observation is not enough to label the data wrong or stale: the mapping's filing status remains unverified, and the download predates the 2026 action. The example instead demonstrates why a current legal-text check and a dataset-version check answer different questions.[^4][^8]

Section 12-10 also contains specifically scoped average/minimum-width and short connecting-portion tests in C5-3, C6-4 and C6-6. Their existence does not establish that the DCM field itself is an average. Its street-setback-line definition gives those lines a limited role for specified regulations; it is not a direction to add a setback strip to every width value.[^17]

**Analytical consequence:** retain mapped width, physical roadbed width, parcel geometry, map effectiveness and legal wide/narrow classification as distinct facts. Their agreement in an ordinary case does not justify merging them into one field. The Allen proceeding is direct evidence of why that separation matters; it is not a general exemption for other streets.

<!-- pagebreak -->

## 6. Resolving a particular frontage without waiting for a universal manual

The public record supports a practical route to a site-specific answer. The following procedure is a research and review workflow, not an automatic legal determination.

1. **Identify the relevant frontage.** Establish the selected lot, the tax-lot-as-zoning-lot assumption and the qualifying street. A nearest-centerline search alone does not establish which street boundary the zoning lot adjoins. Preserve any unresolved lot merger or intervening-land question.

2. **Collect every relevant DCM feature.** Keep the raw labels, feature status, geometry and publication date. For a long or irregular frontage, inspect whether more than one centerline feature is involved. Do not extend one label across a junction or transition solely because the street name remains the same.

3. **Retrieve the map record.** Street Map's public source configuration identifies a Final Section Map index and links to map PDFs. A spatial index match finds candidate sheets; it is not proof that a particular alteration governs the selected frontage. Section Maps and applicable subsequent alterations must be read together.[^7]

4. **Establish the dimension and its status.** Read mapped street lines and stated dimensions at the relevant location. Distinguish adoption, approval and legally required filing. For a uniform portion with a clear dimension and complete effective-map history, the mapped width can be supported directly. A bare image measurement or an old sheet without alteration review has a narrower evidential value.[^12][^16]

5. **Apply the specific zoning provision.** Establish any express street or district exception. Keep a width relation and legal classification separate. Where the frontage crosses a threshold and no applicable method of reducing the variation has been established, that interpretation remains for a supported owner/professional decision.[^17]

Three candidate Section Maps were actually retrieved for the sampled ambiguous records:

| Sampled record | Raw label | Public map document |
|---|---|---|
| East 96 Street, Brooklyn, OBJECTID 183 | `60-75` | [Brooklyn Final Section Map 58](https://nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com/Bk_FS_058.pdf) |
| Walker Street, Manhattan, OBJECTID 1008 | `Unknown but >75` | [Manhattan Final Section Map 10](https://nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com/Mn_FS_010.pdf) |
| Brookville Boulevard, Queens, OBJECTID 8192 | `~75` | [Queens Final Section Map 166](https://nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com/Qns_FS_166.pdf) |

These links resolve document retrieval. They do **not** represent completed present-day frontage determinations for Walker Street or Brookville Boulevard. The map index's `last_date` was not treated as a legal effective date, and ambiguous scan dimensions were not converted into asserted answers.[^5][^19][^20]

For genuinely unclear source annotations, an agency clarification can still be necessary. It is the fallback for a defined unresolved question, rather than a prerequisite to every ordinary mapped-width determination.

<!-- pagebreak -->

## 7. What remains uncertain, and what would close it

The remaining uncertainty is narrower than “nobody knows what street width means.” The mapped-width concept and intentional use of descriptive labels have strong support. The missing link is a general guarantee connecting every annotation to the exact street portion and rule being assessed.

| Open issue | Evidence that would close it | Present disposition |
|---|---|---|
| How a plain number is chosen where width varies | DCP capture instructions specifying the statistic or measurement location, or a supported site-specific map determination | No universal min/max/average rule established |
| Whether a range or bound covers an entire centerline feature | Publisher guidance on feature segmentation and qualifier coverage, or verified mapped bounds covering the actual frontage | Literal annotation retained; spatial guarantee unproven |
| Meaning and tolerance of approximation or probability wording | A documented encoding rule, or independently established map dimensions | No invented tolerance or confidence percentage |
| How to classify an irregular frontage crossing a threshold | The applicable provision and a supported interpretation of its relevant street portion | No unrestricted citywide averaging or minimum rule inferred |
| Allen map amendment's present effectiveness | Required filing evidence and effective date for ACC 30273 | Current zoning exception verified; map filing status not verified |

Two different forms of closure should be named honestly. **Documented publisher semantics** would settle what DCP guarantees about a field. **An approved DRAFT product policy** would settle what the owner authorizes the product to infer under stated conditions. The latter can be a useful operational decision without being misrepresented as the former.

For ordinary individual sites, effective map evidence may close the practical width question even while the universal field question remains open. For ambiguous sites, a defensible result can state the known bounds, the unresolved frontage or interpretation issue, and the rule whose outcome depends on it. This is more informative than either a fabricated exact number or an unexplained generic review label.

The current queue already treats RQ-005's other subparts as closed and retains the encoding/measurement issue. This report supplies stronger affirmative evidence for that remaining item, but does not justify declaring a complete, officially specified DCM decoder.[^6]

<!-- pagebreak -->

## 8. Evidence coverage and limits

The evidence was checked through September 14, 2026 UTC. The DCM full-data profile uses the October 31, 2025 shapefile release, not an asserted September 2026 re-publication. Selected records were separately retrieved from DCP's live ArcGIS service. Agreement between that service and the download corroborates the sampled values, not the currency of every legal map change.[^4][^8]

Publisher evidence includes pinned source files, dataset metadata, migration instructions and original issue/pull-request discussions. Legal evidence includes current definitions, official CPC reports, a BSA decision and the codified City Map provision. Actual Section Map and Alteration Map PDFs were retrieved and visually inspected. Dataset calculations establish formats, lengths and adjacency; they do not establish legal validity.

Targeted Reddit, GIS and architecture-forum searches did not produce a verified firsthand explanation of DCM's universal variable-width convention. The positive public discussion is instead DCP's own developer thread. A practicing architect's published links page also directs readers to Street Map for street-width research, supporting its use as a research tool, without endorsing a particular parser or this report's recommendations.[^3][^21]

The negative finding is deliberately bounded: **no universal convention was located in the materials examined**. It is not proof that no public document, unpublished manual or agency practice exists. Public GitHub code searches do not expose the full upstream editing environment. A title promising width-change visualization, or a metadata field named “Streetwidth,” is not itself a measurement specification.

Some tempting corroboration was withheld. The Tiemann BSA pavement paragraph contains a street-name inconsistency. The Allen report contains inconsistent tax-lot numbering between its narrative and attachment, so it was not used for an automatic parcel join. Historical case lot numbers were not silently equated with current parcel identities. These limitations do not erase the unambiguous mapped-width statements used in the findings.

The companion evidence archive preserves source PDFs and source-response captures, URL/hash metadata where available, selected live JSON records, the original DCM download, and the analysis scripts and tables. Original file bytes are distinguished from computed outputs and connector response captures. A SHA-256 manifest allows file-integrity checks; it does not certify an agency interpretation.

The supported result is therefore specific: mapped-width purpose, intentional text qualifiers and at least one segmented width transition are confirmed; a route to individual map verification is demonstrated; universal field semantics and certain legal applications remain unproven. Further work should target those exact gaps rather than repeat general searches for “NYC street width.”

<!-- pagebreak -->

## Sources

[^1]: NYC Department of City Planning, [DCM Street Center Line ingestion template](https://github.com/NYCPlanning/data-engineering/blob/f2a0f23835215c794d1403b7048e5ba3f42a7201/ingest_templates/dcp_dcmstreetcenterline.yml). Pinned commit `f2a0f23835215c794d1403b7048e5ba3f42a7201`; description, preprocessing and `streetwidt` text declaration. Source blob `f50dc90164c8022871765e6dd6d8734e0ca9781d`.

[^2]: NYC DCP, [Street Map data description](https://github.com/NYCPlanning/labs-streets/blob/18087ee52b3b2847ef64979ae88a6cee9f4f751c/app/templates/data.hbs). Pinned application text, mapped street widths and sidewalk qualification.

[^3]: NYC DCP / Andy Cochran, [Street Map pull request 106](https://github.com/NYCPlanning/labs-streets/pull/106), created and merged April 18, 2018. Description, label-generation patch and embedded Wall Street screenshot. [Original screenshot](https://user-images.githubusercontent.com/409279/38954692-589a6546-4320-11e8-82b6-26e477494320.png).

[^4]: NYC DCP, [Digital City Map shapefile release, October 31, 2025](https://s-media.nyc.gov/agencies/dcp/assets/files/zip/data-tools/bytes/digital-city-map/dcm_20251031shp.zip), `DCM_StreetCenterLine`. SHA-256 `ad21afd2c7c6c2b18dfa76b2776ef896562246437069d52bb4ec5600e575f527`. Counts and adjacency findings are calculations from the captured release, not publisher conclusions.

[^5]: NYC DCP map collection, [Brooklyn Final Section Map 58](https://nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com/Bk_FS_058.pdf). Candidate sheet for the sampled East 96th Street geometry, obtained through the public Final Section Map index. Index date is not asserted to establish legal effectiveness.

[^6]: NYC Buildability, [Research Requests on candidate/D-024-mrl-option-b](https://github.com/martin10101/nyc-buildability/blob/candidate/D-024-mrl-option-b/docs/RESEARCH_REQUESTS.md), RQ-005 and related DRAFT decision requirements. Captured file blob `3016da9fefcb699a6e575a7e7b7af9d55b5e1c0f`; the branch link can change.

[^7]: NYC DCP, [Digital City Map application source configuration](https://github.com/NYCPlanning/labs-layers-api/blob/8e4e8c8e537e8c259e902992048efb22dd0d85d6/data/sources/digital-citymap.json). Pinned width-label handling and Final Section Map index source. The companion archive includes the actual index responses and map URLs used.

[^8]: NYC DCP GIS, [DCM Street Center Line ArcGIS layer](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/DCM_Street_Center_Line/FeatureServer/0). Schema and selected feature queries retrieved September 14, 2026 UTC. The archive retains complete request URLs, response bytes and hashes, including East 96th Street OBJECTIDs 42351, 183, 15472 and 14008.

[^9]: NYC DCP, [Layers API issue 171: Updates CityMap data sources](https://github.com/NYCPlanning/labs-layers-api/issues/171), opened December 17, 2019, closed January 30, 2020. Field extraction instructions. The discussion does not provide a width-entry manual.

[^10]: NYC DCP, [Street Map issue 76: Compute, symbolize, and style where street widths change](https://github.com/NYCPlanning/labs-streets/issues/76), opened April 13, 2018, closed March 6, 2023. Captured body, comments and events do not establish a width algorithm.

[^11]: NYC DCP / Chris Whong, [ZoLa issue 699 discussion](https://github.com/NYCPlanning/labs-zola/issues/699#issuecomment-459476164). Statement about using Street Map labels for widths in ZoLa; evidence of shared presentation sourcing.

<!-- pagebreak -->

## Sources (continued)

[^12]: NYC Administrative Code, [§25-101: City map to be conclusive](https://codelibrary.amlegal.com/codes/newyorkcity/latest/NYCadmin/0-0-0-45640). Current codified text accessed September 14, 2026. The operative qualification concerns duly adopted location, width and grades.

[^13]: NYC Board of Standards and Appeals, [4-07-A](https://www.nyc.gov/assets/bsa/downloads/pdf/decisions/4-07-A.pdf), adopted April 1, 2008, pp. 1–2. Tiemann Avenue Final Map width statement on p. 1; separate pavement discussion has an apparent street-name inconsistency.

[^14]: Bronx Borough President, Engineering Bureau, [Plan 11474, April 18, 1956](https://nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com/cp12444.pdf), amendment to Section 35, grade-change map; Tiemann Avenue between Givan and Tillotson Avenues. The scan labels 60 feet across the outer street lines.

[^15]: NYC DCP, [Geosupport User Programming Guide, Appendix 3](https://nycplanning.github.io/Geosupport-UPG/appendices/appendix03/), entries “STREET WIDTH” and “STREEET WIDTH MAXIMUM” [sic]. Paved-area narrowest/widest-width definitions; a different dataset from DCM.

[^16]: NYC City Planning Commission, [C 250306 MMM: Allen Street Mall Demapping](https://www.nyc.gov/assets/planning/download/pdf/about/cpc/250306.pdf), February 18, 2026, Calendar No. 6. Printed pp. 2–3: mapped configuration and proposed widths; p. 5: unchanged lane layout; p. 8: required filing and effectiveness. Map ACC 30273, September 9, 2025.

[^17]: NYC Zoning Resolution, [§12-10 definitions](https://zr.planning.nyc.gov/article-i/chapter-2/12-10), current official HTML captured September 14, 2026. Relevant entries: street, street line, street setback line, street narrow and street wide. Wide-street definition last amended March 26, 2026. This report is not a substitute for applying the complete definition.

[^18]: NYC City Planning Commission, [N 250307 ZRM: Allen Street Mall Demapping zoning text](https://www.nyc.gov/assets/planning/download/pdf/about/cpc/250307.pdf), February 18, 2026, Calendar No. 7. Explanation and text of the companion wide-street treatment; current enactment checked separately in §12-10.

[^19]: NYC DCP map collection, [Manhattan Final Section Map 10](https://nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com/Mn_FS_010.pdf). Candidate sheet for sampled Walker Street geometry. A current frontage-specific width is not certified by this report.

[^20]: NYC DCP map collection, [Queens Final Section Map 166](https://nycdcp-dcm-alteration-maps.nyc3.digitaloceanspaces.com/Qns_FS_166.pdf). Candidate sheet for sampled Brookville Boulevard geometry. A tolerance for the DCM approximation is not supplied by this retrieval.

[^21]: Jason Little, [The ZRD1 Project: Links](https://www.zrd1.com/links), “Street Width” entry linking Street Map; professional identity described on [About](https://www.zrd1.com/about). Undated pages accessed September 14, 2026. Used only as firsthand evidence of a practitioner research resource.
