# M4-T013 - Street-width / mapped-street official-source research (D-045-R003 B2; A2 dependency)

Producer: official-source-researcher. Date: 2026-09-13. Scope: RESEARCH + registry draft ONLY;
no connector code, no fixtures, no dependency, no schema touched. This report is the research-first
deliverable the later B2 street-width connector packet pins. Quality bar matched:
`project-control/reports/D-040-R001-mappluto-research.md` + `docs/research/source-registry-drafts/pluto-mappluto.json`.
Every material claim carries a live URL + retrieval date; official documentation quoted verbatim;
facts that cannot be evidenced are recorded as open questions, never asserted (permanent principle 3).

Companion deliverable: `docs/research/source-registry-drafts/dcm-street-centerline.json` (two draft
records: ArcGIS primary + SODA fallback).

## 0. Bottom line

- **Authoritative source: the Digital City Map (DCM) - Street Center Line, published by NYC DCP.**
  It is the only official product that records the *mapped* (Official City Map) street width per
  segment together with per-segment geometry and mapped-street status. Two live official channels:
  an ArcGIS feature service (RECOMMENDED PRIMARY) and a Socrata SODA dataset `g6zj-tzgn` (fallback /
  corroboration, currently stale).
- **Geoclient's per-address `streetWidth` is the WRONG concept and is already killed for legal use**
  (paved/roadbed width, not mapped width): 30 ft vs DCM's 60 ft for the same street (West 100 St).
  It may serve only as a free advisory cross-check flag.
- **The single biggest finding: DCM `Streetwidth` is a FREE-TEXT field**, not a clean number - it
  carries ranges (`60-75`), inequalities (`>75`), approximations (`~60`), prose (`Probably between
  80 - 90`), `Width Irregular`, `n/a`, and `Unknown`. Several values straddle the ZR 75-ft cutoff.
  The connector must parse conservatively and fail closed to *narrow* (which preserves the rules
  layer's already-conservative non-wide FAR).
- Recommendation, tradeoffs, and open questions in sections 6-8.

## 1. What the consuming rule needs (the ZR concept), from the repo

The consumer is `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json`
(ZR 23-22, R6/R7-1/R7-2/R8). It computes only the CONSERVATIVE (non-wide-street) FAR and surfaces
the higher wide-street FAR as a conditional alternative it never applies, precisely because "a
wide-street determination is not performed" (rule `limitations`). The rule's own words:

> "Within 100 feet of a wide street (ZR 23-22 footnote 1), a HIGHER standard-residences FAR applies:
> R6 3.00 (vs the conservative 2.20) ... Footnote 1 says 'or portions thereof', so a single lot can
> be split between the two values - a geometry computation, not a table lookup."

"Wide street" is defined in ZR 12-10 (snapshot `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`,
verbatim, content_digest_sha256 `4810adcb...0243a`):

> "A wide street is a street that is 75 feet or more in width. A narrow street is a street that is
> less than 75 feet in width."

So the data input the A2 wave needs is: **per street segment/frontage, the MAPPED street width in
feet (to test >= 75 ft), plus segment geometry (to test the "any portion of the lot within 100
feet of a wide street" condition), plus mapped-street status** (is this an actual mapped street, a
paper street, an unmapped/record street). A single fronting-street width cannot answer footnote 1;
geometry is required. The rule's snapshot note is explicit that the canonical property_profile
exposes NO street-width field today, so this is a genuine new data input.

## 2. Sources investigated and one-line verdicts

| Candidate | What it records | Verdict |
|---|---|---|
| **DCM Street Center Line - ArcGIS** (`DCM_Street_Center_Line/FeatureServer/0`, DCP_GIS) | Mapped width ("widths shown on the Official City Map") + polyline geometry + mapped-street status, per segment | **RECOMMENDED PRIMARY.** Fresh (edited 2025-12-01), keyless, geoJSON-capable, EPSG:2263 native. Free-text width is the caveat. |
| **DCM Street Center Line - SODA** (`g6zj-tzgn`, NYC Open Data) | Same product, tabular + WGS84 geometry | **FALLBACK / corroboration.** Same data but observed STALE (rows ~2024-05) despite a "Monthly" label. |
| **DCM BYTES shapefile** (dcm_street_centerline) | Bulk citywide shapefile | Bulk mirror - forbidden on the thin client; Render-worker only. Exact URL is 403-bound (open question). |
| **Geoclient / Geosupport per-address `streetWidth` / `streetWidthMaximum`** (`api.nyc.gov/geoclient/v2/address`) | Paved/roadbed narrowest width from LION, per address | **KILLED for legal use** (wrong concept, point-not-geometry). Advisory cross-check only. Keyed. |
| **LION** (`lion` FeatureServer / BYTES) | Single-line street base; pavement/roadbed attributes (source of Geoclient's field) | Wrong concept for the ZR mapped-width test; same kill as Geoclient. |

## 3. S1 - Authoritative source identified (with evidence)

**Publisher:** NYC Department of City Planning (DCP). **Product:** Digital City Map (DCM) - Street
Center Line. The DCM "is the official street map of the City of New York" (SODA description, E1;
ArcGIS/metadata Description, E3).

### 3.1 ArcGIS channel (recommended primary) - live-verified 2026-09-13 (E5)
- Endpoint: `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/DCM_Street_Center_Line/FeatureServer/0`
- ArcGIS Online item `9ce5b83f139748f29eb92cdabeb29398` (type Feature Service), owner **DCP_GIS**,
  discovered via `arcgis.com/sharing/rest/search?q=owner:DCP_GIS DCM street` (E4) - same portal that
  serves MapPLUTO and the zoning-features layers.
- geometryType `esriGeometryPolyline`; spatialReference **wkid 102718 / latestWkid 2263** (EPSG:2263,
  NAD83 New York-Long Island, US survey feet); maxRecordCount 2000; currentVersion 12;
  capabilities `Query,Extract`; supportsPagination true; output formats **"JSON, geoJSON, PBF"**.
- **Keyless** (anonymous query succeeded, E5). Access method: standard ArcGIS REST `/query`.
- Freshness: `editingInfo.dataLastEditDate` = 1764617995374 ms = **2025-12-01T19:39:55Z** (E5).

### 3.2 SODA channel (fallback) - live-verified 2026-09-13 (E1)
- Metadata: `https://data.cityofnewyork.us/api/views/g6zj-tzgn.json`; resource:
  `https://data.cityofnewyork.us/resource/g6zj-tzgn.json`. Dataset id `g6zj-tzgn`, name
  `DCM_StreetCenterLine`, attribution DCP, category City Government. Keyless (token optional).
- Update Frequency custom field: "Monthly" (E1). Timestamps (epochs converted 2026-09-13):
  createdAt 2020-05-29; publicationDate 2023-09-28; **rowsUpdatedAt 2024-05-03**; **viewLastModified
  2024-11-01** (E1).

### 3.3 Official metadata (byte-verified from the DCP s-media PDF, E3)
Read directly from `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/dcm_street_centerline.pdf`
(readable PDF; s-media is the authoritative DCP release-document channel). Verbatim:
- Summary: "Citywide street center-line features representing official street names and widths shown
  on the Official City Map of New York City. Dataset last updated: October 31, 2025."
- Use limitations: "Digital City Map (DCM) data changes often and is updated monthly. Updates will
  include recent city map alterations adopted by City Council. This dataset is provided by the
  Department of City Planning (DCP) on DCP's website for informational purposes only. DCP does not
  warranty the completeness, accuracy, content, or fitness for any particular purpose or use of the
  dataset ... DCP and the City are not liable for any deficiencies ...".
- Spatial Reference: WKID 102718 / LatestWKID 2263, NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet.
- Object count 53986; Creation date 2020-05-15; Publication date 2025-10-31.

Nothing here is guessed: the publisher, endpoints, auth posture, CRS, and cadence are all from the
source's own live services and its own metadata document.

## 4. S2 - Width semantics pinned (which width, units, ZR mapping)

**Which width concept:** DCM records the width **as shown on the Official City Map** - i.e. the
legally *mapped* street width. This is the concept ZR 12-10 turns on (the street as mapped, not the
pavement). This characterization comes from the dataset Summary/Description (E3); however - stated
honestly - **there is NO field-level definition of `Streetwidth` in the official metadata** (the
field entry lists only alias/type/width, E3). The mapped-width interpretation therefore rests on
(a) the "Official City Map" framing and (b) empirical divergence from paved width (section 5). The
exact geometric definition (mapped right-of-way / property-line-to-property-line vs bed) is **OQ-1**
- byte-verify against the Official City Map / borough final-section source at full validation.

**Units:** feet, where the value is numeric (consistent with the sibling DCP products and the
75-ft ZR threshold). Byte-verified field definitions for the other columns (Feat_Type, Street_NM,
Route_Type, Record_ST, Paper_ST, Stair_ST, CCO_ST, Marg_Wharf) are captured verbatim in the
registry draft's `field_definitions_byte_verified_from_metadata_E3` block.

**The field is FREE TEXT (central finding, E7).** A grouped-count enumeration of `streetwidt`
(2026-09-13) shows, alongside clean integers, the following non-numeric classes:
- `n/a` (2954), `Unknown` (1404), `Width Irregular` (45), `varies`/`Varies`, `Regular but unknown.`
- inequalities: `>80` (368), `>75` (364), `>100`, `<60`, `<50`, ...
- ranges: `60-75` (18), `50-60` (21), `75-90` (7), `75-100` (3), `74-75.3` (1), `166-192`, ...
- approximations/prose: `~60` (62), `~80`, `Around 100`, `More or less 40`, `Probably between 80 - 90`
- decimals: `49.5`, `66.05`, `114.96`, ...
- hedged unknowns straddling the cutoff: `Unknown but <75` (38), `Unknown but >75` (17)

**Mapping onto the ZR threshold (the consumer named):** the rules layer needs a binary wide (>= 75 ft)
/ narrow (< 75 ft) classification per segment (ZR 12-10), then a geometry test for "within 100 ft of
a wide street, or portions thereof" (ZR 23-22 footnote 1). Because a wide-street determination only
ever *raises* FAR, the safe direction is to classify a segment "wide" **only when the value is
unambiguously >= 75 ft**. Any ambiguous value (`60-75`, `74-75.3`, `>60`, `~70`, `Width Irregular`,
`n/a`, `Unknown`, `Unknown but <75`, and even `Unknown but >75` until a policy resolves it) must fail
closed to **narrow**, so the rule's already-conservative non-wide FAR is never overridden by a guess.
The exact fail-closed policy for each ambiguity class is a ZR-grounded rule/legal decision (**OQ-3**),
not a data-cleaning decision - recorded as an open question, not resolved here by assumption.

## 5. S4 - Honest comparison vs Geoclient per-address streetWidth

Recorded Geoclient fields (fixture `services/api/tests/fixtures/geoclient/G01_address_documented_example.json`,
314 W 100 St -> BBL 1018887502): `streetWidth` = "30", `streetWidthMaximum` = "30",
`streetStatus` = "2", plus segment attributes (`segmentLengthInFeet`, `numberOfTravelLanesOnTheStreet`,
`roadwayType`, `speedLimit`).

| Axis | Geoclient/Geosupport `streetWidth` | DCM Street Center Line |
|---|---|---|
| Concept | Paved/roadbed width (from LION). Search-derived definition (E2/pilot): "the narrowest width, in feet, of the paved area of the street." Byte-verification of that exact wording still owed (LION field dictionary is deep in a 1.3 MB PDF; the field is confirmed a LION-sourced Extended-Function work-area-2 output in the Geosupport UPG, E8). | Mapped width shown on the Official City Map (the legal concept ZR 12-10 uses). |
| Same street, W 100 St Manhattan | 30 (E-fixture) | 60 and 100 across two segments (E6) - reproduces the pilot's 30-vs-60 divergence. |
| Granularity | Per address / fronting blockface; a single scalar; NO geometry. | Per segment; carries polyline geometry - the ingredient the within-100-ft, around-the-corner, any-portion-of-lot test needs. |
| Authority for the ZR test | None - measures pavement, systematically UNDER-reports the mapped width, would flip legal answers near 75 ft in both directions. | The mapped-width source the ZR test intends. |
| Auth | Keyed (Ocp-Apim-Subscription-Key; owner-provisioned). | Keyless. |
| Failure modes | Wrong concept silently returns a plausible number; per-address only, cannot express segment variation (W 100 St is 60 AND 100). | Free-text width (ambiguity); paper/unmapped/irregular segments; +/-20 ft accuracy class; segment-vs-lot geometry work still required. |

**Disagreement surface:** for any street whose paved width and mapped width straddle 75 ft, Geoclient
and DCM give opposite legal answers. Geoclient's field is therefore **killed for direct legal use**
(consistent with the already-recorded kill in `docs/research/source-registry-drafts/geoclient.json`
and the pilot `docs/research/street-width-source-pilot-2026-09-11.md`). It may be retained only as a
free advisory cross-check flag (e.g. "paved width disagrees materially with mapped width - review"),
never as the determinant.

## 6. S3 - Re-runnable thin-client capture procedure

Design only (no capture executed under repo scope beyond the small verbatim samples quoted here;
sized for the thin client - KB-scale, no bulk downloads).

**Primary (ArcGIS), per segment/area:**
```
GET https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/DCM_Street_Center_Line/FeatureServer/0/query
    ?where=<bounded predicate, e.g. Borough='Manhattan' AND Street_NM='West 100 Street'>
    &outFields=OBJECTID,Borough,Feat_Type,Feat_status,Street_NM,Streetwidth,Route_Type,Build_Status,Record_ST,Paper_ST,Edit_Date
    &returnGeometry=true&outSR=2263&f=json          # native feet for measurement
    &orderByFields=OBJECTID ASC&resultRecordCount=<=2000&resultOffset=<n>
```
- For display transport only, request `f=geojson&outSR=4326` (never for measurement - mirror the
  MapPLUTO two-CRS discipline: measurement stays in EPSG:2263).
- Recording: save the raw response bytes verbatim; record retrieval timestamp (file write time, per
  the M2-T021 correction) and `sha256(raw_response_bytes)`; pin provenance with
  `editingInfo.dataLastEditDate` from `/0?f=json`. Honor `exceededTransferLimit` for paging; treat an
  HTTP-200 body carrying an ArcGIS `error` object as an upstream error, never as data (zoning-features
  finding).

**Fallback / corroboration (SODA):**
```
GET https://data.cityofnewyork.us/resource/g6zj-tzgn.json?$where=borough='Manhattan' AND street_nm='West 100 Street'&$limit=50
GET https://data.cityofnewyork.us/api/views/g6zj-tzgn.json      # columns array + viewLastModified freshness signal
```
- SODA omits null fields per record - derive schema from the api/views columns array, never record
  keys. `the_geom` here is WGS84; do not mix CRS. Same timestamp+sha256 recording.

**Representative raw samples captured 2026-09-13 (small, verbatim):**
- SODA record: `{"borough":"Staten Island","feat_type":"Mapped_St","feat_statu":"City_St","street_nm":"Ellis Street","streetwidt":"90","route_type":"Gen_use","roadway_typ":"Surface_ST","build_stat":"Improved","the_geom":{"type":"MultiLineString",...}}` (E1)
- West 100 St Manhattan (SODA): two segments, `streetwidt` "60" and "100", both Feat_Type Mapped_St,
  Feat_statu City_St, Build_Stat Improved (E6).

**Auth posture:** both DCM channels are **keyless** - no key requirement, nothing routed to the owner
boundary for this source. (Geoclient, by contrast, is keyed; but it is not the recommended source.)

## 7. S5/S6 - Registry draft + scope

- Registry draft written: `docs/research/source-registry-drafts/dcm-street-centerline.json`, two
  records (`nyc-dcp-dcm-street-centerline-arcgis` primary; `nyc-dcp-dcm-street-centerline-soda`
  fallback), cloning the M2-T009 posture of `pluto-mappluto.json` (source_id, agency, endpoint,
  auth, rate_limits, update_frequency, geographic_coverage, fields_available, terms, connector
  PLAN-ONLY, limitations, fallback_source, open_questions) with a `draft_status` marker making the
  non-final status explicit. No invented registry mechanism; consistent with this report.
- Scope: research + drafts only. Zero code, fixtures, dependencies, or schema touched (S6). See the
  self-checks in section 9.

## 8. Recommendation, tradeoffs, open questions

**Recommendation for the later B2 connector packet:** build the street-width connector against the
**DCM Street Center Line ArcGIS feature service** as primary (fresh, keyless, geoJSON-capable,
EPSG:2263 native, per-segment geometry), with the SODA `g6zj-tzgn` dataset as a corroboration/
fallback channel carrying a documented staleness caveat, and the BYTES shapefile reserved for any
future citywide import on a Render worker. Retain Geoclient `streetWidth` only as a non-authoritative
advisory cross-check.

**Top tradeoff (stated, not hidden):** the authoritative width field is **free text**, so the
connector cannot simply read a number. It must implement a conservative parser that classifies a
segment "wide" only on an unambiguous >= 75 ft value and fails closed to "narrow" on every ambiguous,
ranged, irregular, `n/a`, or `Unknown` value. This preserves the rules layer's conservative posture
(it never over-states FAR) at the cost of under-claiming wide-street eligibility for genuinely-wide
streets whose DCM value is messy - which is the correct direction for a legally sensitive tool, but
it means DCM alone will leave some real wide-street lots conservatively rated until the width value
(or a geometry-derived width) is resolved. Secondary tradeoff: ArcGIS currency vs SODA convenience -
the SODA channel is easier to query in bulk but is ~16 months stale, so currency must come from
ArcGIS.

**Open questions (carried into the registry draft; none resolved by assumption):**
1. OQ-1: byte-verify the exact geometric definition of DCM mapped width (no field-level metadata
   definition exists); confirm mapped-ROW vs bed.
2. OQ-2: value domains for Feat_statu, RoadwayTyp, Build_Stat.
3. OQ-3: the ZR-grounded fail-closed classification policy for every free-text-width class,
   irregular/paper/unmapped segments (a rule/legal decision, needs G6-class review).
4. OQ-4: the within-100-ft-of-a-wide-street, any-portion-of-lot geometry computation (DCM line
   geometry x lot geometry x 100-ft buffer) - a separate downstream task; fronting width alone
   cannot answer ZR 23-22 footnote 1.
5. OQ-5: exact BYTES shapefile download URL/file name (nyc.gov 403 to non-browser clients; browser
   capture needed; must not be guessed).
6. OQ-1a: whether the SODA channel is effectively deprecated (its "Monthly" label disagrees with its
   observed 2024 timestamps).
7. Byte-verify the LION `streetWidth` "narrowest width of the paved area" wording (E2 search-derived;
   confirmed UPG-sourced but exact LION field text not byte-read).

## 9. Self-checks (documented_test_commands)

Run in the worktree; results recorded verbatim in the return to the orchestrator. Docs-only change,
both must stay EXIT 0.
- `python tools/validate_directive_compliance.py --check`
- `python tools/modularity_check.py --check`

## Evidence index (all retrieved 2026-09-13 unless noted)

- E1 - SODA metadata `https://data.cityofnewyork.us/api/views/g6zj-tzgn.json` (columns array,
  timestamps, Update Frequency) + sample records `https://data.cityofnewyork.us/resource/g6zj-tzgn.json?$limit=2`
- E2 - LION StreetWidth "narrowest width of the paved area of the street" - search-derived via the
  pilot `docs/research/street-width-source-pilot-2026-09-11.md` (cites `lion_metadata.pdf`); NOT
  byte-verified verbatim (open question 7).
- E3 - Official DCM metadata PDF `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/dcm_street_centerline.pdf`
  (byte-read: Summary, Use limitations, Spatial Reference, verbatim field definitions).
- E4 - ArcGIS Online search `https://www.arcgis.com/sharing/rest/search?q=owner:DCP_GIS DCM street&f=json`
  (item id + service URL).
- E5 - ArcGIS layer metadata `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/DCM_Street_Center_Line/FeatureServer/0?f=json`
  (geometryType, CRS, maxRecordCount, formats, dataLastEditDate, row count).
- E6 - West 100 St Manhattan query `https://data.cityofnewyork.us/resource/g6zj-tzgn.json?$where=borough='Manhattan' AND street_nm='West 100 Street'` (60 and 100).
- E7 - `streetwidt` grouped-count domain `https://data.cityofnewyork.us/resource/g6zj-tzgn.json?$select=streetwidt,count(*)&$group=streetwidt&$order=count(*) desc`.
- E8 - Geosupport UPG `https://nycplanning.github.io/Geosupport-UPG/chapters/chapterV/section05/`
  (Street Width / Street Width Maximum are Extended Function 1/1E work-area-2 fields; detail in
  Appendix 13 - not byte-read here).
- E-fixture - `services/api/tests/fixtures/geoclient/G01_address_documented_example.json`
  (streetWidth "30", streetWidthMaximum "30").
- ZR 12-10 snapshot `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`; consumer rule
  `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json`.
