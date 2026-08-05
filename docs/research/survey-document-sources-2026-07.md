# Survey & Official-Document Source / Format Research — Packet A (M2-T014)

- **Task:** M2-T014 (research-only; owner directive 2026-07-20, survey workstream Packet A; dispatch hold lifted by owner 2026-08-04).
- **Producer:** official-source-researcher.
- **Scope:** INVENTORY official systems that may provide surveys / site plans / tax maps / architectural
  filings / related documents; DISTINGUISH the seven document classes; feed the format policy
  (`docs/SURVEY_DOCUMENT_FORMAT_POLICY.md`) and registry rows.
- **Retrieval anchor:** all live retrievals **2026-08-05 UTC** (server-clock anchor from response
  `Date`/`Last-Modified` headers; local session date 2026-08-04). Every citation is retrieval-date-stamped.
- **Fixtures:** `docs/research/fixtures/m2-t014/` (verbatim extracts + reproducible curl commands).
- **Hard rule honored:** official public sources only. No login/CAPTCHA/viewer-control/bandwidth-policy
  bypass is documented or designed. Where no authorized stable URL/API exists, the finding is recorded as
  **manual upload required**. Any credential/payment/terms-ambiguity is recorded as a STOP finding, not
  acted on.

---

## 0. Executive summary (SR-S1)

| # | Official system | What it can supply | Authorized programmatic access? | Finding |
|---|---|---|---|---|
| 1 | **DOF Digital Tax Map (DTM)** — ArcGIS FeatureServer + Open Data layers | tax-lot polygons, tax-block polygons, condo/air/sub/REUC lot tables, tax-map sheet index | **YES** (anonymous ArcGIS REST + Socrata SODA) | **AVAILABLE** |
| 2 | **DOF DTM tax-map sheet PDFs** (Property Information Portal `map_library`) | scanned/rendered official tax-map sheets (PDF) | Reachable URL but **generation-stamped, not documented as stable**; portal is a human viewer | **RESTRICTED** (treat as manual/where-documented only) |
| 3 | **DOB filing metadata** (DOB NOW / BIS via NYC Open Data) | job/permit/CO records, BBL/BIN linkage — **not the drawings** | **YES** for the metadata (prior tasks M1-T007/M1-T008; registry §6/§7) | **AVAILABLE (metadata only)** |
| 4 | **DOB plans / drawings / site plans** (DOB NOW Public Portal viewer; BIS microfilm; records request) | site plans, architectural drawings, plot plans in filings | **NO** documented API; viewer-only for some newer digital uploads, else in-person / records request | **RESTRICTED → manual upload required** |
| 5 | **ACRIS document images** (`a836-acris.nyc.gov` viewer) | scanned recorded instruments (deeds, and any *recorded* survey/map exhibits) | **NO** — register **detects & blocks automated capture**; bulk = paid subscription | **NO AUTHORIZED PROGRAMMATIC ACCESS → manual upload required** (SR-S5) |
| 6 | **ACRIS index metadata** (NYC Open Data / Socrata) | document metadata + **BBL→document_id linkage** — not the images | **YES** (Socrata SODA) | **AVAILABLE (metadata only)** |
| 7 | **DCP datasets** (MapPLUTO tax-lot geometry, GIS Zoning Features, building footprints) | administrative lot geometry, footprints — **no surveys/site plans** | **YES** (registry §2/§4) | **AVAILABLE (not survey evidence)** |
| 8 | **Licensed boundary / topographic surveys** (sealed by a NYS-licensed land surveyor) | the authoritative boundary/topography document | **NONE** — not held in any public City system; private (owner/surveyor) | **NO PUBLIC SYSTEM → manual upload required** (SR-S5) |

**Bottom line for the M2-T015 ingestion pipeline:** the single most authoritative class (a *licensed
boundary/topographic survey*) exists in **no** public system, and the richest scanned-document channels
(ACRIS images, DOB plans) have **no authorized programmatic retrieval**. The pipeline must therefore be
built around **user upload of the document the applicant already holds**, with the public systems used only
for (a) administrative lot geometry/tax-map context (DTM, MapPLUTO — available) and (b) metadata linkage
(ACRIS index, DOB filing metadata — available). This is the empirical justification for the "manual upload
required" posture the owner directive anticipated.

---

## 1. DOF Digital Tax Map (DTM) — AVAILABLE

### 1.1 What it is
NYC Department of Finance's official cartographic tax map: the shape, location and identity of every tax
lot and tax block, plus condominium, air-lot, subterranean-lot and real-estate-of-utility-company (REUC)
lot tables and a tax-map-sheet index. It is a **tax-administration cartographic product**, not a survey
(see §9, class 3).

### 1.2 Authorized access channels (retrieved 2026-08-05 UTC)

**(a) ArcGIS REST FeatureServer — primary programmatic channel (AVAILABLE, anonymous).**
`https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer`
(`?f=pjson` retrieved 2026-08-05). Layers/tables observed verbatim:

- Layer 0 `TAX_LOT_POLYGON`, Layer 1 `TAX_BLOCK_POLYGON` (polygon feature layers).
- Tables 2–19: `AIR_LOT`, `CONDO`, `CONDO_UNIT`, `REUC_LOT`, `SUB_LOT`, `MAPLIBRARY_HAB`,
  `MAPLIBRARY_MAP`, `DAB_BOOK_HEADER`, `DAB_AIR`, `DAB_BLOCK`, `DAB_BOUNDARY`, `DAB_CONDO`,
  `DAB_CONDO_UNIT`, `DAB_LOT`, `DAB_REUC`, `DAB_SUB`, `PTS_DESC_DAILY`, `PTS_CONDO_DAILY`.
- `spatialReference wkid 102100 / latestWkid 3857` (**EPSG:3857 Web Mercator** — DIFFERENT from the DCP
  production chain's EPSG:2263; CRS must be validated before any coordinate math or cross-source overlay).
- `maxRecordCount 1000` (per-request page cap → paging mandatory for any bulk read).

Per-BBL query proven live (fixture `dtm_taxlot_query_1000010010.json`, HTTP 200):
`.../FeatureServer/0/query?where=BBL='1000010010'&outFields=BBL,BORO,BLOCK,LOT,LOT_NOTE,EFFECTIVE_TAX_YEAR&returnGeometry=false&f=json`
→ `{"BBL":"1000010010","BORO":"1","BLOCK":1,"LOT":10,"LOT_NOTE":null,"EFFECTIVE_TAX_YEAR":"2026-2027"}`.
Response headers (fixture `dtm_taxlot_query_headers.txt`) publish a rate signal
`x-esri-org-request-units-per-min: usage=23;max=28800` and `Last-Modified: Tue, 04 Aug 2026 14:27:51 GMT`
(read-only replica freshness signal).

**(b) NYC Open Data / Socrata layers — AVAILABLE.** The DTM has been republished on Open Data as a growing
collection of its layers/tables. `TAX_LOT_POLYGON` = dataset `i38t-6if2`
(`https://data.cityofnewyork.us/api/views/i38t-6if2.json`, retrieved 2026-08-05): `provenance official`,
attribution "Department of Finance (DOF)", 17 columns
(`the_geom`, `BORO`, `BLOCK`, `LOT`, `BBL`, `CONDO_FLAG`, `REUC_FLAG`, `AIR_LOT_FLAG`, `SUB_LOT_FLAG`,
`EASEMENT_FLAG`, `LOT_NOTE`, `EFFECTIVE_TAX_YEAR`, `BILL_BBL_FLAG`, `NYCMAP_BLDG_FLAG`,
`CONVERSION_EXCEPTION_FLAG`, `VALUE_REFLECTED_OUT_FLAG`), created 2024-10-16. Official data dictionary
attached: `DOF-DigitalTaxMap-Relational-Data-Dictionary.xlsx` (assetId
`e044ecb0-689c-498c-a7de-432a54cb8c9a`; XLSX content extraction deferred to a cloud environment — same
octet-stream constraint as the DOB dictionaries, prior OQ-2).

**(c) Legacy blob download — RETIRING.** Dataset `smk3-tmxj`
(`https://data.cityofnewyork.us/api/views/smk3-tmxj.json`, retrieved 2026-08-05) is an `assetType file`
blob whose description states verbatim **"This downloadable file will be retired by October 2025"** and
directs users to the Digital Tax Map Collection. Do NOT build on this blob; it is superseded by (a)/(b).

### 1.3 Cadence / freshness
Official statement (Open Data description + metadata): data is **extracted from DOF's internal system
monthly** and **refreshed on ArcGIS Online on the 1st of each month** (search-corroborated wording:
"extracted ... on the last Friday of each month and refreshed on ArcGIS Online on the 1st"). Freshness
signals: ArcGIS `Last-Modified` header (2026-08-04 observed) + Socrata `rowsUpdatedAt` on the layer
datasets + `EFFECTIVE_TAX_YEAR` per feature. **No permanence/SLA is assumed** (registry governance rule 2).

### 1.4 Known limitations
- Tax-lot polygons are a **cartographic/administrative** boundary, **not a legal survey** (class 2 vs 1,
  §9) — near-boundary conclusions must be typed uncertain.
- CRS is EPSG:3857 here, **not** the EPSG:2263 of the DCP chain — mixing without reprojection is a defect.
- `maxRecordCount 1000` — citywide reads require deterministic paging (Render worker; never local).

---

## 2. DOF tax-map SHEET PDFs (Property Information Portal `map_library`) — RESTRICTED

The DOF Property Information Portal serves rendered/scanned official **tax-map sheet PDFs** at
`https://propertyinformationportal.nyc.gov/pdf/home/index/map_library/<id>`. One example fetched live
2026-08-05 (`.../map_library/10047420250312125816`) returned **HTTP 200, `application/pdf`, ~2.0 MB**.
The path segment embeds what appears to be a lot/block key plus a **generation timestamp**
(`...20250312125816` ≈ 2025-03-12 12:58:16), i.e. the URL is **generation-stamped, not documented as a
stable addressable identifier**. The portal itself is a **human viewer**; there is no official API
documentation enumerating these URLs.

**Finding:** treat tax-map sheet PDFs as **RESTRICTED** — usable only where a human obtains the specific
sheet through the portal and uploads it, or where DOF later publishes a documented stable endpoint. Do NOT
guess or enumerate these URLs programmatically. The machine-provenance tax-map geometry channel is §1
(DTM FeatureServer / Open Data); the sheet PDF is a presentation artifact.

---

## 3. DOB filing metadata (DOB NOW / BIS via NYC Open Data) — AVAILABLE (metadata only)

DOB **filing/permit/CO records** are already inventoried and registered (this platform's accepted research
`docs/research/M1-T007-dob-now-sources.md`, `docs/research/dob-legacy-sources.md`;
`docs/SOURCE_ACCESS_REGISTRY.md` §6 DOB NOW family, §7 BIS/legacy family). These Socrata datasets carry
BBL/BIN linkage and filing history but **contain no drawings** — they are the *metadata* substrate that
lets us know a filing/plan set exists for a BBL/BIN, and lets us cite it, without providing the plan image
itself. No new endpoint is verified here; this section only records the boundary: DOB Open Data =
metadata, **not** the plan documents (which are §4).

---

## 4. DOB plans / drawings / site plans — RESTRICTED → manual upload required (SR-S5 candidate)

### 4.1 Finding
There is **no authorized programmatic API** that returns DOB architectural drawings, site/plot plans, or
approved plan sets for arbitrary properties. Retrieval channels (search-verified 2026-08-05):

- **DOB NOW Public Portal** (`a810-dobnow.nyc.gov`, "DOB NOW: Public Portal", official user manual
  `www.nyc.gov/assets/buildings/pdf/DOB_NOW_public_portal_manual.pdf`): a **human viewer** where *some
  newer* DOB NOW filings include digital plan uploads that can be viewed online. No documented API; access
  is via the interactive portal only.
- **Most approved plans are NOT online.** Official guidance
  (`www.nyc.gov/site/buildings/property-or-business-owner/info-for-property-owners.page` and the DOB
  **Records Request User Guide** `www.nyc.gov/assets/buildings/pdf/records_request_user_guide.pdf`):
  approved plans are stored at the **DOB borough office** (microfilm / digital plan records); viewing
  requires an in-person visit or a formal **records request** via DOB NOW: BIS Options, **logged in with an
  eFiling account**.

### 4.2 Disposition
- Programmatic retrieval of DOB plans = **not available**. Do NOT scrape the public portal or design any
  login/records-request automation.
- eFiling-account records requests are behind a **login** → **STOP condition** (credentialed access; not
  automated by this platform).
- Product posture: **manual upload required** — the applicant/architect uploads the DOB plan/site plan they
  already hold or retrieved. The DOB Open Data metadata (§3) provides the citation/provenance that such a
  filing exists.

---

## 5. ACRIS document IMAGES — NO AUTHORIZED PROGRAMMATIC ACCESS → manual upload required (SR-S5)

### 5.1 Finding (decisive, verbatim-evidenced)
The Automated City Register Information System (ACRIS, DOF) holds **scanned images of recorded real-property
instruments** (deeds, mortgages, and any *recorded* survey/map exhibits) for the five boroughs (Manhattan
from 1966; other boroughs generally from 2003). The **document images are served only through the ACRIS
viewer** (`a836-acris.nyc.gov`), which **actively blocks automation**:

- `GET https://a836-acris.nyc.gov/DS/DocumentSearch/Index` (2026-08-05) → **HTTP 307** →
  `Location: https://a836-acris.nyc.gov/BandwidthPolicy/ACRIS-BW-POL.html` (fixture
  `acris_viewer_307_headers.txt`).
- That official **ACRIS Bandwidth Notice** (retrieved 2026-08-05) references **"detection of automated
  scripts/robots that are capturing data from the website"** and blocking clients that **"exceeded the
  bandwidth limits we have established"**, and directs bulk needs to **"contact the City Register
  (Ph: 212-487-6300) to learn about our subscription data services"**, pointing casual users to NYC Open
  Data for *index* data.

### 5.2 Disposition
- ACRIS document images: **no authorized programmatic access.** Automated capture is **explicitly
  prohibited** by the official policy. This platform must **never** design or document any path that
  evades it.
- The "subscription data services" route = **payment** → **STOP condition** (do not procure; owner-only
  action if ever proposed).
- Product posture: **manual upload required** — if a recorded survey/map exhibit or deed is needed, a human
  obtains it through the ACRIS viewer under the site's terms and uploads it. Metadata linkage comes from
  §6.

This is the primary **SR-S5 negative case**: a system investigated and honestly recorded as having **no
authorized programmatic access**, alongside the licensed-survey case (§7) and DOB plans (§4).

---

## 6. ACRIS INDEX metadata (NYC Open Data / Socrata) — AVAILABLE (metadata only)

The ACRIS **index** (not the images) is published on NYC Open Data and is programmatically available.
Verified live 2026-08-05:

- **ACRIS - Real Property Master** `bnx9-e6tj` (`api/views` retrieved 2026-08-05): `provenance official`,
  attribution DOF, columns `document_id, record_type, crfn, recorded_borough, doc_type, document_date,
  document_amt, recorded_datetime, modified_date, reel_yr, reel_nbr, reel_pg, percent_trans,
  good_through_date`. **No column contains an image URL** — metadata only; `crfn`/`reel_*` are pointers
  into the physical/viewer record, not a fetchable image.
- **ACRIS - Real Property Legals** `8h5j-fqxa` (`api/views` retrieved 2026-08-05): `provenance official`,
  columns `document_id, record_type, borough (number), block (number), lot (number), easement,
  partial_lot, air_rights, subterranean_rights, property_type, street_number, street_name, unit,
  good_through_date`; ~22.7M rows. **This is the BBL→document_id join**: given a BBL we can enumerate the
  `document_id`s recorded against it, then a human retrieves the image via the ACRIS viewer (§5).

Related ACRIS index datasets exist (Parties, References, Remarks, Document Control Codes, Personal Property
family) — all metadata, all Socrata, all image-free; not individually re-verified here (same platform
baseline as registry §5 governance).

**Access mode:** Socrata SODA (platform baseline in `docs/SOURCE_ACCESS_REGISTRY.md` §governance rule 5).
**Use:** provenance/citation + linkage only; **never** presented as the document itself.

---

## 7. Licensed boundary / topographic surveys — NO PUBLIC SYSTEM → manual upload required (SR-S5)

The authoritative boundary/topographic document is a **survey sealed by a New York State licensed land
surveyor** (NYS Education Law Article 145). Such surveys are **commissioned privately** and held by the
property owner, their surveyor, title company, or lender. They are **not maintained in any public NYC
system**:

- DOF DTM / MapPLUTO publish **administrative tax-lot polygons**, explicitly **not** legal survey boundaries
  (class 2, §9; DCP's own "±20 ft, not for lot-level determination" caveat, registry §2/§4).
- DOB filings may *contain* a plot/site plan referencing a survey, but DOB does not publish the underlying
  licensed survey as a retrievable dataset (§4).
- A licensed survey is only in ACRIS if it happened to be **recorded** as an exhibit — and even then the
  image is viewer-gated (§5), not programmatic.

**Finding:** there is **no authorized public system** — programmatic or otherwise — that yields the
licensed survey for an arbitrary property. Product posture: **manual upload required** (the owner supplies
the survey they hold). This is the honest core of Packet A and the reason M2-T015 is an upload pipeline,
not a scraper.

---

## 8. Related-but-not-survey official systems (recorded for completeness)

- **DCP MapPLUTO / GIS Zoning Features** — administrative lot geometry + zoning; AVAILABLE; registry §2/§4.
  Provides lot shape context, **not** survey/site-plan evidence.
- **NYC building footprints** (OTI/DoITT, published on NYC Open Data) — footprint polygons; AVAILABLE via
  Socrata; **not** a survey (a footprint is a mapped building outline, not a boundary determination). Not
  re-verified in depth here; recorded as an available context layer for M2-T015 to consider, subject to its
  own G1.
- **ZoLa / NYC Property Information Portal viewers** — human presentation layers; **never** machine
  provenance (registry governance rule 1). The tax-map sheet PDF (§2) is reached *through* the portal.

---

## 9. The SEVEN document classes (SR-S2) — definitions, evidentiary weight, NON-interchangeability

These are related evidence sources but are **NOT interchangeable**. Conflating them is a legal-integrity
defect. Each class below states what it **can** and **cannot** establish.

| # | Class | Definition | Evidentiary weight | Can establish | CANNOT establish | Public source? |
|---|---|---|---|---|---|---|
| 1 | **Licensed boundary / topographic survey** | Field survey sealed by a NYS-licensed land surveyor; boundary lines, monuments, dimensions, encroachments, easements, and (topographic) elevations/contours | **Highest** — the authoritative statement of actual property boundaries & topography | Legal lot boundaries, actual dimensions, encroachments, easements, grade/topography | Zoning/use rights; what is *proposed* | **None** — private; manual upload (§7) |
| 2 | **Tax-lot polygon** | DOF DTM / DCP MapPLUTO administrative polygon of a tax lot (`the_geom`, BBL) | **Administrative/cartographic** — ±accuracy; for tax mapping & GIS context | Approximate lot shape/location for identification & mapping; BBL identity | **Legal boundaries** (explicitly not survey-grade; DCP ±20 ft); precise dimensions | **Yes** — DTM/MapPLUTO (§1) |
| 3 | **Tax map** | DOF's official tax-map **sheet** (cartographic representation of blocks/lots, dimensions shown for tax admin) | **Administrative** — DOF's cartographic record, not a survey | Block/lot identity, tax-map dimensions/annotations, easement notations *as mapped* | Legal boundary determination; on-the-ground conditions | **Restricted** — sheet PDF via portal (§2); geometry via DTM (§1) |
| 4 | **DOB site plan** | Plot/site plan within a DOB filing showing site layout (existing/proposed) prepared by the applicant's design professional | **Applicant-submitted** — self-certified; regulatory-submission weight, not independent survey | What the applicant *represented* to DOB for the site layout of a filing | Independent boundary truth (not a surveyor's determination); guaranteed as-built | **Restricted** — viewer/records request; manual upload (§4) |
| 5 | **Architectural drawing** | Floor plans, elevations, sections, details in a DOB/architect filing | **Design document** — professional design intent | Design/layout intent, dimensions *as drawn*, egress/use as filed | Property boundaries; that construction matches the drawing | **Restricted** — manual upload (§4) |
| 6 | **Proposed plan** | Any drawing depicting a design **not yet built or not yet approved** (proposed condition) | **Aspirational** — lowest as-built weight; a proposal only | The design *intent* under consideration | **Existing/as-built conditions**; approval; legal boundaries | **Restricted** — manual upload (§4) |
| 7 | **Historical filing attachment** | Older BIS/microfilm plans or documents attached to a past filing | **As-of-filing-date snapshot** — may be superseded | Conditions/representations **as of that historical filing** | Current conditions (may be superseded by later work); legal boundaries | **Restricted** — borough office/microfilm; manual upload (§4) |

**Non-interchangeability rules (must be enforced downstream):**
1. A **tax-lot polygon** or **tax map** (classes 2–3) **never** substitutes for a **licensed survey**
   (class 1) in any boundary/dimension conclusion. They are administrative approximations.
2. A **DOB site plan** (4) is **not** a surveyor's boundary determination; it is an applicant
   representation. It never upgrades to class 1.
3. A **proposed plan** (6) **never** establishes existing/as-built conditions; existing conditions require
   a survey (1) or an as-built/historical record (7), each with its own weight.
4. A **historical filing attachment** (7) is time-stamped to its filing and may be **superseded**; it never
   speaks to current conditions without corroboration.
5. Every class carries its **class label + source provenance + retrieval timestamp**; the platform must
   never silently promote a lower-weight class to a higher one. AI classifies and drafts; deterministic
   code and qualified humans decide legal weight (CLAUDE.md principle 1).

---

## 10. Access-rule summary (SR-S4) — authorized retrieval vs manual upload

| Source | Authorized stable URL / API (cited) | Retrieval preserves | Else |
|---|---|---|---|
| DTM tax-lot/block geometry | `services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer/{0,1}/query` (ArcGIS REST) + Socrata `i38t-6if2` | URL, retrieval timestamp, response headers (`Last-Modified`, rate units), MIME `application/json`, digest of raw response | — |
| ACRIS index metadata | Socrata `bnx9-e6tj`, `8h5j-fqxa` (`data.cityofnewyork.us/resource/<id>.json`) | URL, timestamp, `rowsUpdatedAt`, MIME, digest | — |
| DOB filing metadata | registry §6/§7 Socrata datasets (prior tasks) | as above | — |
| DTM tax-map **sheet PDF** | portal URL is generation-stamped, **not documented as stable** | — | **manual / where a human obtains the specific sheet** |
| DOB plans / site plans / drawings | **none** (viewer + eFiling login + records request) | — | **manual upload required** |
| ACRIS document **images** | **none** (viewer; automation explicitly prohibited; bulk = paid) | — | **manual upload required** |
| Licensed boundary/topographic survey | **none** (private) | — | **manual upload required** |

No endpoint above is guessed; each "AVAILABLE" URL was fetched live 2026-08-05 (fixtures + inline
citations). Each "none" is recorded as **manual upload required**, never as a bypass.

---

## 11. STOP conditions hit (recorded, not acted on)

- **ACRIS subscription data services** (§5) = **payment** → STOP; not procured; owner-only if ever proposed.
- **DOB records request via eFiling** (§4) = **credentialed login** → STOP; not automated.
- **Terms-of-use:** ACRIS terms are **not ambiguous** on this point — automated capture is expressly
  prohibited; recorded and honored. No external emails were sent. No accounts were created.

## 12. Open questions (for M2-T015 / G1)

- OQ-A1: DTM XLSX data dictionary (`e044ecb0-...`) field-level semantics — extract in a cloud environment.
- OQ-A2: Whether DOF ever publishes a **documented stable** endpoint for tax-map sheet PDFs (currently
  generation-stamped only, §2).
- OQ-A3: Depth/coverage of DOB NOW Public Portal digital plan uploads (which filings have viewable plans) —
  requires the browser viewer; not scriptable.
- OQ-A4: Building-footprints dataset (§8) full G1 identity/cadence if M2-T015 elects to use it as context.
