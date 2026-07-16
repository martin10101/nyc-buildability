# M1-T001 fetch evidence (orchestrator-captured, 2026-07-16)

The producer sandbox denied all network tools (producer report §3). Per the 2026-07-15 evidence-capture directive the orchestrator executed the producer's §5 fetch plan. Every item below is from a live fetch/search on **2026-07-16**; WebFetch answers are produced by a summarizer model over the fetched page — the producer should treat direct quotes as evidence and paraphrases as pointers to re-verify at the cited URL if load-bearing.

## E1 — PLUTO Open Data dataset metadata (fetch: `https://data.cityofnewyork.us/api/views/64uk-42ks.json`)

- Name: "Primary Land Use Tax Lot Output (PLUTO)"; ID **64uk-42ks**; attribution "Department of City Planning (DCP)"; category "City Government"; viewType tabular/table; provenance "Official"; created 2020-02-12.
- Description: "Extensive land use and geographic data at the tax lot level in comma-separated values (CSV) file format. The PLUTO files contain more than seventy fields derived from data maintained by city agencies."
- Summarizer reported "Last Updated: August 26, 2026 / Publication Date: July 30, 2026" — **future-dated relative to retrieval; timestamps need re-verification from the raw JSON** (likely misconverted unix values). OPEN QUESTION for producer/G1.

## E2 — PLUTO SODA resource endpoint LIVE (fetch: `https://data.cityofnewyork.us/resource/64uk-42ks.json?$limit=1`)

- Returns a valid JSON record. **`version` field value: "26v1"** — the Open Data tabular channel currently serves the same version as the DCP bulk release.
- Full field list returned (73 fields, verbatim): borough, block, lot, cd, ct2010, cb2010, schooldist, council, zipcode, firecomp, policeprct, healtharea, sanitboro, sanitsub, address, zonedist1, splitzone, bldgclass, landuse, easements, ownername, lotarea, bldgarea, comarea, resarea, officearea, retailarea, garagearea, strgearea, factryarea, otherarea, areasource, numbldgs, numfloors, unitsres, unitstotal, lotfront, lotdepth, bldgfront, bldgdepth, ext, proxcode, irrlotcode, lottype, bsmtcode, assessland, assesstot, exempttot, yearbuilt, yearalter1, yearalter2, builtfar, residfar, commfar, facilfar, affresfar, mnffar, borocode, bbl, tract2010, xcoord, ycoord, latitude, longitude, zonemap, sanborn, taxmap, plutomapid, version, sanitdistrict, healthcenterdistrict, bct2020, bctcb2020, transitzone.
- NOTE: the one sampled record did NOT surface zonedist2-4, overlay1-2, spdist1-3, ltdheight, landmark, histdist, appbbl, condono etc. — SODA omits null fields per record; the full column set must be taken from the data dictionary / api/views columns array, not from a single record. OPEN QUESTION: confirm full SODA column list via `/api/views/64uk-42ks.json` columns array.

## E3 — MapPLUTO Open Data dataset metadata (fetch: `https://data.cityofnewyork.us/api/views/f888-ni5f.json`)

- Name: "Primary Land Use Tax Lot Output - Map (MapPLUTO)"; ID **f888-ni5f**; attribution DCP.
- Description: "Comprehensive land use and geographic data at the tax lot level in GIS format... merged with tax lot features from the Department of Finance's Digital Tax Map, clipped to shoreline."
- viewType/displayType: **href** — attachment/external-link distribution, NOT a tabular SODA resource. Update frequency metadata: "Quarterly".
- Attachments listed: `PLUTODD22v3.pdf`, `PlutoReadme22v3.pdf` (STALE 22v3 attachments on the portal — current dictionaries live on DCP's site, see E4; this is a channel-lag observation for S4).
- Raw timestamps reported: created/rowsUpdated/publication all 1374771826/1374771872 (2013-07-25) — href datasets don't update row timestamps; version currency must come from the DCP channel.

## E4 — Official README 26v1 (fetch: `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_readme.pdf`, 342 KB PDF, read pages 1-8 directly)

Verbatim/near-verbatim findings:
- Header: "PLUTO README DOCUMENT — May 2026 (26v1)".
- "The Primary Land Use Tax Lot Output (PLUTO™) data file contains extensive land use and geographic data at the tax lot level in an ASCII comma-delimited file." Fields derived from DCP, DOF, DCAS, LPC.
- **Release model:** "There are two types of PLUTO updates: major and minor. Major updates occur quarterly, and all fields are updated. A major update is represented first digit in the version number after 'v', for example 24v1. Minor updates are released monthly between major updates and only include updates to the zoning attributes. A minor release is represented by the decimal after the version number – 24v1.1, 24v1.2, etc." Minor-release fields: ZoneDist1-4, Overlay1-2, SPDist1-3, LtdHeight, SplitZone, ResidFAR, CommFAR, FacilFAR, ZoneMap, ZMCode, TaxMap, EDesigNum.
- **Condo semantics:** "PLUTO data contain one record per condominium complex instead of records for each condominium unit tax lot... The Condominium Complex record is assigned the 'billing' tax lot number when one exists. When the 'billing' tax lot number has not yet been assigned by DOF, the lowest tax lot number within the tax block of the Condominium Complex is assigned." APPBBL logic updated in 25v1.1→25v2 range: condo lots without direct APPBBL now inherit from an associated condo unit lot.
- **Geography idiosyncrasy:** Marble Hill legally Manhattan/serviced by Bronx; Rikers legally Bronx/serviced by Queens.
- **DATES OF DATA table (26v1):** DCP E-Designations 2026-04-01; Zoning Map Index 2019-07-01; City Owned/Leased 2025-03-31; NYC GIS Zoning Features 2026-03-31; Political/Admin Districts 26A 2026-04-01; **Geosupport version 26A** 2026-04-01; DOF Digital Tax Map (DTM) 2026-04-03; DOF CAMA 2026-03-02; DOF PTS 2026-03-30; Parks GreenThumb 2026-04-14; LPC Landmark+Historic District Building DB 2026-02-03; LPC Individual Landmarks 2026-02-02; OTI Building Footprint Centroids 2026-03-29.
- "City Planning also merges the PLUTO data with the DCP modified version of the DOF's Digital tax map to create MapPLUTO for use with various geographic information systems."
- Disclaimer: "PLUTO is being provided by the Department of City Planning (DCP) on DCP's website for informational purposes only. DCP does not warranty the completeness, accuracy, content, or fitness for any particular purpose or use..."
- **New fields in 26v1** (vs 25v4): MIHOption1-4 (Mandatory Inclusionary Housing option flags), TrnstZone (Transit Zone classification), AffResFAR (max affordable residential FAR), ManuFAR (max manufacturing FAR). New zoning district value C6-12. (City of Yes-related FAR updates noted in 25v2 changes.)
- Null convention example: "NUMBER OF FLOORS (NumFloors) has been modified to show <null> for values of zero and for other values of less than one."
- Change file: "The changes made to a tax lot record are records in PLUTOChangeFile<ver>.csv, which is available as part of the MapPLUTO download on BYTES of the BIG APPLE."

## E5 — Data dictionary 26v1 located (search-verified title)

- "PLUTO DATA DICTIONARY May 2026 (26v1)" at `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` (search result title string confirms version+date). Producer: cite this as the authoritative field/units/null reference; field-level extraction still to do (fetch as PDF and read pages as needed).

## E6 — DCP page + archive + formats (search evidence, 2026-07-16)

- Current DCP page: `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change` (title: "PLUTO, MapPLUTO and PLUTO Change File"); legacy URL `https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page` still resolves in search. **nyc.gov and apps.nyc.gov content-api return HTTP 403 to this session's WebFetch** (bot protection) — page-level claims (download sizes, exact archive links) are OPEN for G1 re-verification via browser or the content-api from a permitted network.
- MapPLUTO formats (search summary + meta_mappluto.pdf title): ESRI shapefile and File Geodatabase; Shoreline **Clipped** (`Mappluto/Mappluto.gdb`) and **Unclipped water-included** (`Mapplutounclipped/Mapplutounclipped.gdb`); borough shapefile distribution exists. Prior versions: "All previously released versions of this data are available on the DCP Website: BYTES of the BIG APPLE."
- Official build pipeline (open source): `https://github.com/NYCPlanning/db-pluto` + docs `https://nycplanning.github.io/db-pluto/`.
- ArcGIS Hub item exists (`https://hub.arcgis.com/datasets/DCP::mappluto-1/about`) but page is JS-rendered — feature-service endpoint UNVERIFIED; OPEN QUESTION.

## E7 — SODA auth/rate limits (fetch: `https://dev.socrata.com/docs/app-tokens`)

- App tokens **optional**: "Without a token: requests are throttled by IP address and share a common pool." With a token: "we do not throttle API requests that are using an application token, unless those requests are determined to be abusive or malicious." Throttled requests → HTTP 429. Pass via `X-App-Token` header (preferred) or `$$app_token` param. No numeric published limit for tokened requests.

## Channel priority implication for S4 (producer to argue from evidence)

PLUTO tabular: SODA resource (64uk-42ks) live and version-current (26v1) → good API-tier channel; bulk CSV from DCP for full-file imports. MapPLUTO geometry: NO tabular SODA; official channel = DCP bulk FileGDB/shapefile (clipped/unclipped), Open Data f888-ni5f is an href pointer with stale attachments; ArcGIS service unverified. Portal attachment staleness (22v3 dictionary on f888-ni5f) is a concrete cross-channel discrepancy to record.
