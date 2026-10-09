> [Receiving-session note, 2026-09-13, D-050-R002 / D-051-R004: owner-returned independent
> confirmation research for RQ-005, received via the D-050 channel and archived verbatim below
> as a DISCOVERY AID. It is NOT provenance: every load-bearing claim must be captured from the
> official source under the normal discipline before encoding. Its evidence package stays with
> the owner (thin client). Queue stamps: docs/RESEARCH_REQUESTS.md RQ-005.]

# RQ-005 Street Width Verification

**RQ-005(1) should remain open for the precise geometric measurement convention and the meaning of variable or unusual width entries.** Stronger official evidence now supports three narrower findings: the product describes mapped street widths; sidewalk inclusion is stated as usual; and the City's application displays the width values in feet. Those findings do not amount to a complete specification for converting every record into a zoning determination.[^1][^2][^3]

The existing answers to RQ-005(2), the exact DCM bulk download, and RQ-005(3), LION's pavement-width definition, stand. This follow-up addresses the remaining DCM field question and supplies additional evidence for it. It is a research handoff under the existing DRAFT and professional-review process.

## Findings and disposition

| Question | Finding | Disposition |
|---|---|---|
| Does DCM describe mapped widths? | The dataset describes widths shown on the Official City Map. | Supported at product level.[^1] |
| Are sidewalks included? | The official application's description says they usually are. | Supported with that qualification.[^2] |
| What units does the application use? | Official map-source code appends `ft` directly to the source width text. | Feet supported as intended display units.[^3] |
| Is every value measured between a precisely defined pair of boundaries? | No complete field-level specification was located in the identified official publications. | Open. |
| Does a variable-width value mean minimum, maximum, nominal or frontage-specific width? | Real records include ranges, approximations and irregular-width descriptions; no complete interpretation specification was located. | Open. |
| Are all text encodings formally defined? | Neither the published metadata source nor the inspected service/schema supplies a width code list. | Open.[^4][^6][^8] |
| Is an undocumented field equivalent to no public documentation anywhere? | A bounded publication search cannot establish that universal negative. | Do not make that claim. |

## Official metadata evidence

The current DCM Street Center Line metadata PDF identifies the intended product as widths from the Official City Map. Its width-field entry on page 4 gives `Streetwidt` a string type and storage width of 50, but no description. The number 50 is field capacity, not a measurement in feet. The shapefile's embedded XML also lacks an explanatory width-field definition.[^1]

The most useful additional source is DCP's public metadata-authoring repository. Its `products/dcm/street_center_line/metadata.yml` identifies the same shapefile layer, `DCM_StreetCenterLine`, and links the official metadata PDF. Its entire width entry is:[^4]

```yaml
- id: streetwidt
  name: Streetwidt
  data_type: text
```

Several neighboring fields have both descriptions and enumerated values. This field has neither. The matching file in DCP's data-engineering repository has identical content. Fourteen historical versions associated with commits touching this metadata file, from September 10, 2024 through June 1, 2026, retain the same three-line entry. The evidence archive contains those versions and their URL/hash audit.[^4][^5]

The metadata source contains a possible spreadsheet dictionary artifact, but its relevant attachment configuration is commented out and the listed Socrata destination is marked unpublished. That is a lead about publication configuration, not proof that a public spreadsheet with the missing definition exists. A retained March 2024 date in its descriptive text also cannot establish the current data release date.[^4]

The public ArcGIS layer supplies a nullable text field named `Streetwidth`, length 50, with a null domain. Its item-level metadata XML repeats the product description without a width-specific definition. The older NYC Open Data table uses `streetwidt` and has an empty column description; its catalog notice says updates there are paused and directs readers to DCP's download page. These are different publication surfaces, with different field names and update histories.[^6][^7][^8]

## What the City's application establishes

The official Street Map application's data-help source says:

> "Mapped street widths (usually includes sidewalks)"

The word **usually** matters. This is stronger evidence than a generic assumption that a street-width field must represent the pavement. It does not support changing the statement to "always includes every sidewalk" or "always equals current property-line-to-property-line distance."[^2]

The official map-layer configuration selects the DCM source field and adds a feet suffix:

```sql
COALESCE('   (' || streetwidt || ' ft)') AS streetwidth
```

The expression reads from `dcp_dcm_street_centerline`. It establishes a direct connection between the width attribute and the publisher's intended display units. It displays the source text; it does not define a minimum/maximum selection procedure, an approximation tolerance, or a zoning classification algorithm. The configuration's descriptive update label says December 2022, so that label should not be used as proof of the service's current release.[^3]

The correct refined description is therefore: **DCM publishes mapped street-width information, generally including sidewalks, which the official application displays in feet. The exact boundary and text-encoding conventions still need an authoritative specification.**

## Observed values in the official data

A grouped query of the official ArcGIS service, captured September 13, 2026, counted 54,051 features. A separate total-count query returned the same number. The grouped response contained 954 width labels. Independently reading the verified October 2025 shapefile's attribute table produced the same row total and counts below. The shapefile has 955 distinct text values because it retains both `Varies` and `varies`, while the service grouping combines their four records.[^6][^9]

Of these 54,051 rows, **6,908, or 12.8%, do not match plain integer/decimal syntax**. This is a descriptive parsing statistic, not the percentage of legally unclassifiable streets. An inequality can convey useful information without being a plain number; the unresolved issue is its authoritative interpretation and applicability. The population includes all feature types in the product, not just the frontage records a particular project would use.[^6][^9]

| Exact source text | Number of records | What is still needed |
|---|---:|---|
| `n/a` | 2,954 | Applicable feature/status convention; do not turn it into a numeric width. |
| `Unknown` | 1,401 | Authoritative width evidence. |
| `>80` | 368 | Meaning and spatial applicability of the stated bound. |
| `>75` | 364 | Meaning and spatial applicability of the stated bound. |
| `~60` | 62 | Approximation convention and tolerance. |
| `Width Irregular` | 45 | Location-specific width evidence and interpretation. |
| `Unknown but <75` | 38 | Basis and spatial coverage of the bound. |
| `60-75` | 18 | Whether/how the range applies along the segment and frontage. |
| `Unknown but >75` | 17 | Basis and spatial coverage of the bound. |
| `~75` | 9 | Approximation tolerance near the zoning threshold. |

The unusual entries are not confined to contextual unmapped records. A targeted query returned the following examples, all marked `Mapped_St`, with `Feat_status` equal to `City_St`, and `Record_ST` and `Paper_ST` both `N`:[^6]

| Service OBJECTID | Street and borough | Width text |
|---|---|---|
| 183 | East 96 Street, Brooklyn | `60-75` |
| 380 | Shore Parkway North, Queens | `Width Irregular` |
| 474 | Margaret Corbin Drive, Manhattan | `Unknown but <75` |
| 1008 | Walker Street, Manhattan | `Unknown but >75` |
| 8192 | Brookville Boulevard, Queens | `~75` |

These are examples of individual service records, not statements about the entire named street. OBJECTIDs identify the captured service version and should not be assumed permanent across later republishes. The evidence archive contains the complete query responses, URLs and exact-count profile.

## Measurement boundaries

Mapped street boundaries and present physical or ownership boundaries should be distinguished. DCP's Street Map explanation says built streets may be narrower than their mapped dimensions and that some mapped streets have never been built. It identifies adopted Section Maps and Alteration Maps as the components documenting the City Map.[^10]

A concrete historical illustration appears on page 5 of DCP's February 2016 Bay Street Corridor boards. The board distinguishes mapped and built widths and identifies privately owned lots and buildings lying within the mapped street bed. That example supports caution about equating a mapped width with the space between today's tax-lot boundaries. Its old zoning numbers are not used as current rules here.[^11]

The unresolved specification should explain which mapped boundaries supply the attribute, how those boundaries relate to other right-of-way or ownership lines, and how a width applies to different points along a centerline feature. A product-level statement about mapped widths does not answer all three. A site-specific adopted map can resolve a particular location without necessarily resolving the field convention for the entire city.

## Implications for the build

The evidence supports retaining the original width text, source/version and feature-status fields separately from any parsed number or classification. A parsed scalar, an interval, an approximation, an unknown value and a zoning conclusion are different pieces of information. This is an engineering recommendation; it does not authorize an interpretation decision or change the project's existing owner/professional gates.

For example, mechanically extracting the first number from `Unknown but <75` would discard the inequality. Turning `60-75` into its first or last endpoint would impose an unverified rule. Treating `~75` as an exact threshold would discard the stated approximation. The official data confirms that these are concrete input cases.

An unknown width also should not be presented as a factually verified narrow street. A conservative fallback must be justified for each consuming rule. The general upper-building setback rule uses 15 feet for narrow streets and 10 feet for wide streets, but the general street-wall placement rule requires 70% within ten feet on narrow streets and eight feet on wide streets, subject to its exceptions. Consequently, a smaller capacity estimate alone does not prove that every generated geometry or compliance result is conservative.[^12][^13]

The build can continue on supported rule families and clearly labeled assumptions within its existing process. RQ-005(1) should retain a precise factual gap rather than being closed on the basis of application display code. Conversely, it should no longer be described as if the mapped scope, usual sidewalk inclusion and intended display units had no supporting official evidence.

## Evidence needed to close the remaining question

The strongest remaining target is DCP's authoring convention or data dictionary for the width field. The published PDF lists **DCPOpendata@planning.nyc.gov** as the dataset contact. That is a direct starting point for locating the responsible GIS or mapping staff.[^1]

An authoritative document or written clarification should identify:

1. The exact dataset and field names, product versions, units, measurement boundaries, and any feature-type exceptions.
2. Whether a scalar width is a mapped dimension, nominal width, minimum, maximum or other representation, especially where the street changes width.
3. How ranges, inequalities, approximations, irregular-width labels, missing values and `n/a` are authored and interpreted.
4. How those values apply spatially along a feature and to a particular frontage, including junctions and unequal or nonparallel boundaries.
5. Which adopted map record controls when the attribute is uncertain or inconsistent, and how to locate that record.

The request should include actual examples such as `60-75`, `~75`, `Unknown but >75` and `Width Irregular`. Asking only whether sidewalks are included would leave much of the remaining question unanswered. The resulting specification would close the factual research gap only to the extent that it answers those conventions; its use for a particular zoning determination remains subject to the project's interpretation process.

## Scope and limitations

This verification combines official metadata publications and their bounded history, application descriptions and source configuration, original shapefile attributes, live service/schema responses, and mapping explanations. It also checks the older Open Data publication so that stale metadata is not mistaken for the current source. The observed ArcGIS data-edit timestamp is December 1, 2025; the bulk file is labeled October 31, 2025. The matching width counts do not establish that every other field or geometry in the two products is identical.

The reviewed metadata history covers one identified public file across 14 revisions. It does not prove that DCP has never documented the convention in another publication, attachment, historical repository or internal manual. The defensible conclusion is **"not located in the identified sources"**, not "the City never wrote it down" or "further web research cannot solve it."

## Sources

[^1]: NYC Department of City Planning, [Digital City Map - Street Center Line metadata PDF](https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/dcm_street_centerline.pdf), dataset date October 31, 2025; pp. 1, 2 and 4. Original PDF and embedded shapefile XML preserved in the evidence package.

[^2]: NYC Department of City Planning, [Street Map data-help source](https://github.com/NYCPlanning/labs-streets/blob/18087ee52b3b2847ef64979ae88a6cee9f4f751c/app/templates/data.hbs), commit 18087ee5, item "Mapped street widths." Same wording present in the captured official application bundle.

[^3]: NYC Department of City Planning, [Digital City Map source configuration](https://github.com/NYCPlanning/labs-layers-api/blob/8e4e8c8e537e8c259e902992048efb22dd0d85d6/data/sources/digital-citymap.json), commit 8e4e8c8e, source layer `street-centerlines`; descriptive update label December 2022.

[^4]: NYC Department of City Planning, [Street Center Line metadata-authoring file](https://github.com/NYCPlanning/product-metadata/blob/2a84b24d0f0b9d97e2c964ba59b3d190f2870c11/products/dcm/street_center_line/metadata.yml), commit 2a84b24d. Matching [data-engineering copy](https://github.com/NYCPlanning/data-engineering/blob/f2a0f23835215c794d1403b7048e5ba3f42a7201/product-metadata/products/dcm/street_center_line/metadata.yml). Both identify Git blob 16c1f7e53b7c108ab6b572cfce43ff86ee65666e.

[^5]: NYC Department of City Planning, [commit history for the metadata file](https://api.github.com/repos/NYCPlanning/product-metadata/commits?path=products%2Fdcm%2Fstreet_center_line%2Fmetadata.yml&per_page=100), 14 returned revisions dated September 10, 2024 through June 1, 2026. Each captured version and its URL/hash are in `agent_docs/field_history_results.json` in the evidence package.

[^6]: NYC Department of City Planning, [DCM Street Center Line service layer](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/DCM_Street_Center_Line/FeatureServer/0), schema and read-only grouped, total-count and example-record queries captured September 13, 2026. Exact query URLs, response bytes and hashes are supplied in the evidence package.

[^7]: NYC Department of City Planning, [ArcGIS item metadata XML](https://www.arcgis.com/sharing/rest/content/items/9ce5b83f139748f29eb92cdabeb29398/info/metadata/metadata.xml), item 9ce5b83f139748f29eb92cdabeb29398; owner DCP_GIS; captured September 13, 2026.

[^8]: NYC Open Data / Department of City Planning, [DCM Street Center Line table metadata](https://data.cityofnewyork.us/api/views/g6zj-tzgn.json) and [catalog record](https://data.cityofnewyork.us/City-Government/DCM_StreetCenterLine/g6zj-tzgn); data timestamp May 3, 2024; metadata timestamp November 1, 2024; update-pause notice retained in the captured catalog response.

[^9]: NYC Department of City Planning, [DCM October 2025 bulk shapefile ZIP](https://s-media.nyc.gov/agencies/dcp/assets/files/zip/data-tools/bytes/digital-city-map/dcm_20251031shp.zip), internal `DCM_StreetCenterLine.dbf`. The original ZIP SHA-256 is recorded in the evidence manifest; the included profiling script reproduces the width counts from its attribute table.

[^10]: NYC Department of City Planning, [Street Map City Map explanation](https://github.com/NYCPlanning/labs-streets/blob/18087ee52b3b2847ef64979ae88a6cee9f4f751c/app/templates/city-map.hbs), commit 18087ee5.

[^11]: NYC Department of City Planning, [Bay Street Corridor boards](https://www.nyc.gov/assets/planning/downloads/pdf/our-work/plans/staten-island/bay-street-corridor/160219_bsc_boards.pdf), February 2016, p. 5, "Designated Street Widths." Historical illustration of mapped versus built conditions only.

[^12]: NYC Zoning Resolution, [23-433 Standard setback regulations](https://zr.planning.nyc.gov/article-ii/chapter-3/23-433), current official text checked September 13, 2026.

[^13]: NYC Zoning Resolution, [23-431 Street wall location requirements](https://zr.planning.nyc.gov/article-ii/chapter-3/23-431), paragraph (b) and applicable exceptions, current official text checked September 13, 2026.
