<!-- Orchestrator capture header: official-source-researcher return saved VERBATIM
     (transport entity-decoding only: &gt;/&lt;/&amp; decoded). Dispatched 2026-09-19
     (session seq 119) against backlog row DB-026; delivered same day. The researcher's
     worktree lacked the current DB-026 row text and geoclient_address.py (its flag #10);
     orchestrator confirmed the findings match the current row before saving. -->

I have complete, authoritative coverage. Final failure-semantic evidence: GeoSearch returns `match_type:"fallback"` and `confidence:0.8` on BOTH the exact live-case hit AND total-nonsense inputs (nonexistent street "1279 zzqqxx street" → returns "1279 53/57/68 Street" on wrong streets; out-of-range "99999" → returns "207 37 Street"). So neither field discriminates success — only comparing the returned `housenumber`+`street` to the input does. PAD Open Data (bc8t-ecyu) `rowsUpdatedAt` is frozen at 2015 (blobby file), so PAD freshness comes only from `addendum.pad.version` (live: **26c**). Here is my report.

---

# DB-026 Source Reconnaissance: authoritative address→tax-lot for range/corner addresses + address-of-record

**Producer:** official-source-researcher · **Retrieval date:** 2026-09-18 (all live probes and doc fetches this date) · **Scope:** read-only external research; no repo files written.

**Live-verified vs doc-only labelling:** `[LIVE]` = I executed the request this session and quote the actual response. `[DOC]` = quoted from official documentation, not executed live (e.g., Geoclient, which requires a subscription key I do not hold).

**Note on context files:** the three files named in the task (`docs/DISCOVERY_BACKLOG.md` row DB-026, `docs/research/live-case-regression-properties.md`, `services/api/app/connectors/geoclient_address.py`) are **not present in my worktree** — it is based off an older commit whose `connectors/` dir has only `bbl.py`, `pluto_soda.py`, `mappluto_geometry_arcgis.py`, `zoning_features_arcgis.py`, `ztldb_soda.py`. I grounded instead in the accepted prior research `docs/research/M0-T002-geoclient-address-resolution.md` (Geoclient/GeoSearch/Geoservice/GDE) and `connectors/bbl.py`. Flagging so the orchestrator can confirm nothing in the newer DB-026 row contradicts this.

---

## Root cause of the live case (verified)

`[LIVE]` **MapPLUTO** (`64uk-42ks`) for BBL 3052960043 stores exactly one address:
```
GET https://data.cityofnewyork.us/resource/64uk-42ks.json?$where=bbl='3052960043'
→ {"bbl":"3052960043.00000000","address":"3622 13 AVENUE","borough":"BK","block":"5296","lot":"43","bldgclass":"K4","zonedist1":"M1-2/R6A","ownername":"3622 THIRTEENTH LLC",...}
```
`[DOC]` **PLUTO Data Dictionary, Aug 2026 (26v2), p.13, field ADDRESS** — the authoritative definition of the "address of record":
> Format: Alphanumeric – 28 characters. **Data Source: Department of Finance – Property Tax System (PTS).** Description: "An address for the tax lot. Tax lots may be assigned a single house number on a street, a range of house numbers on a street, or addresses on multiple streets. **ADDRESS contains the address in PTS, using the low number when there is a range of house numbers.** ... **A complete list of the addresses assigned to a tax lot is available through Geosupport or by downloading the Property Address Directory (PAD)** ..."

So PLUTO/PTS deliberately keeps **one** address per lot (the DOF billing/record address, low-number-of-range). Corner lot 3052960043 has its record address on its 13 Avenue frontage ("3622 13 AVENUE"); its 37 Street frontage ("1279 37 STREET") exists only in PAD/Geosupport. A pipeline that matches against the PLUTO address string alone therefore cannot resolve "1279 37 Street". This is a documented, expected data property — not a data error.

---

## Findings per source

### 1. NYC Geoclient API v2 — RECOMMENDED PRIMARY (address→BBL)
- **Owner/operator:** NYC Office of Technology & Innovation (OTI), wrapping DCP **Geosupport**, "NYC's official geocoder of record." Base URL `https://api.nyc.gov/geoclient/v2`. `[DOC]`
- **Auth:** subscription key required, header `Ocp-Apim-Subscription-Key: <key>`, obtained free at `https://api-portal.nyc.gov/` (Geoclient User product, "Geoclient - v2"). **Human action required** — I could not run live Geoclient probes. `[DOC]`
- **Function/endpoints for this task:**
  - `/v2/search?input=<free text>` (single-field; parses unstructured input, dispatches to Function 1B/BL/BN). Recognises a bare 10-digit string as a BBL and 7-digit as a BIN. `[DOC]`
  - `/v2/address?houseNumber=&street=&borough=` (Geosupport **Function 1B**). `[DOC]`
  - `/v2/bbl?borough=&block=&lot=` (Function BL) and `/v2/bin?bin=` (Function BN) for reverse validation/expansion. `[DOC]`
- **How it handles corner/range/vanity addresses (the DB-026 requirement):** Function 1B resolves the input house number against Geosupport's **address ranges** (the same PAD/Street-Name-Dictionary data), so a secondary-frontage house number like "1279 37 Street" resolves to the lot even though it is not the PLUTO address. Geosupport also performs **vanity-address normalization** (documented example: input "314 W 100 St" → "280 RIVERSIDE DRIVE"). `[DOC, M0-T002]`
- **BBL fields returned & meaning** (from official example responses): `bbl` (10-digit), `bblBoroughCode`, `bblTaxBlock` (5, zero-padded), `bblTaxLot` (4, zero-padded), `buildingIdentificationNumber` (BIN), plus `condominiumBillingBbl`, `lowBblOfThisBuildingsCondominiumUnits`/`highBblOfThisBuildingsCondominiumUnits` for condos. Canonical address echoed as `houseNumber` + `firstStreetNameNormalized`/`boePreferredStreetName` (this is the normalized form of the **input**, not the lot's record address). `[DOC, M0-T002]`
- **Status/ambiguity semantics:** HTTP 200 always for a reached request; the geocoding outcome is in Geosupport Return Codes (GRC): `00` success, `01` success-with-warning (`message` populated), `>01` reject. `/address` has **two** sub-calls — check both `returnCode1e`/`reasonCode1e`/`message` (1E) and `returnCode1a`/`reasonCode2`/`message2` (1A). Ambiguity/failure GRCs: `EE`+reason = similar-street suggestions; `11` = not recognized/no similar names; `50` = invalid street for this location; `75` = duplicate address (pseudo-street); `63` = non-unique intersection. `[DOC, M0-T002 / Geosupport UPG App.4]`
- **Rate limits / cadence:** official rate limits **not published** (visible only inside the portal after sign-in — UNKNOWN, needs G1). Data currency = the Geosupport release loaded on the server; query `/v2/version` for the release id. Underlying PAD/Geosupport releases quarterly (`<YY><A–D>`) with biweekly UPAD/TPAD interim updates. `[DOC]`
- **Limitation for DB-026:** Geoclient returns the normalized **input** address + BBL + BIN; it does **not** by itself return the lot's PLUTO/PTS "address of record." That still requires a BBL→PLUTO.Address lookup (see §6).

### 2. NYC Planning Labs GeoSearch v2 — RECOMMENDED CROSS-CHECK (keyless; verified on the live case)
- **Owner:** NYC DCP (Planning Labs); Pelias over a normalized **PAD** extract. Base `https://geosearch.planninglabs.nyc/v2/`, endpoints `/search`, `/autocomplete`. **No key.** `[DOC + LIVE]`
- **BBL/BIN path:** `properties.addendum.pad.{bbl,bin,version}`. Text-search only — cannot validate a bare BBL/BIN input. `[DOC + LIVE]`
- **Freshness signal:** `addendum.pad.version` (live = **"26c"**). The Open Data PAD mirror timestamp is unusable: `[LIVE]` `bc8t-ecyu` `rowsUpdatedAt=1433788337` = 2015-06-08 (frozen blobby-file `createdAt`).
- **Failure semantics — load-bearing finding `[LIVE]`:** `match_type` and `confidence` do **not** discriminate success. The exact live-case hit returned `"match_type":"fallback","confidence":0.8`; a nonexistent street ("1279 zzqqxx street brooklyn") returned three fallback features on **wrong streets** ("1279 53/57/68 STREET") also at `fallback`/`0.8`; an out-of-range house number ("99999 37 street brooklyn") returned "207/213 37 STREET"; a bare street ("37 street brooklyn") returned arbitrary points. **The only reliable success test is field equality:** compare the returned `properties.housenumber` and normalized `properties.street` to the requested house number and street before trusting the BBL.

### 3. DCP PAD (Property Address Directory) — the underlying data both Geoclient and GeoSearch use
- **Owner:** DCP Geographic Systems Section (GSS). Distributed as two ASCII comma-delimited files. Open Data id `bc8t-ecyu` is a **file download, not a queryable SODA table** (`api/views` returns zero columns) — do not attempt `$where` queries against it. `[LIVE + DOC]`
- **Two files (official layout, s-media `padlayout.pdf` + guide `padgui.pdf`) `[DOC]`:**
  - **ADR (Address) file** — one row per address/frontage of a lot. Fields incl. `boro`/`block`/`lot` (FK to BBL file), `bin` (7), `lhnd`/`hhnd` = **"Low/High Housenumber Display Format of Address Range"** (char 12), `lhns`/`hhns` sort format (11), `lcontpar`/`hcontpar` continuous-parity, `lsos`/`hsos` side-of-street, `stname` (32), `addrtype` (1), `parity` ('0'=NAP,'1'=odd,'2'=even), `realb7sc` (real street of a vanity address), `segid` (LION segment id), `zipcode`.
  - **BBL file** — one row per tax lot. Fields incl. `boro`/`block`/`lot`, condo range `loboro…hilot`, condo billing BBL `billboro…billlot`, `condoflag` ('C'), `condonum`/`coopnum`, **`numbf` = Number of blockfaces for the lot**, **`numaddr` = Number of addresses for the lot (max 2500)**, `vacant` ('V'), `interior` ('I').
- **Corner / multiple-frontage handling (RQ1 core) `[DOC, padgui p.1]`:** PAD's list identifies "so far as the information is known, **all** of the buildings the lot contains; **all** of the street addresses and non-addressable street frontages of each of those buildings; **all** of the street frontages of the lot not associated with buildings." A corner lot therefore yields **multiple ADR rows** (one per frontage/entrance), reflected in `numaddr`/`numbf`. This is exactly why PAD has both "3622 13 AVENUE" and "1279 37 STREET" for BBL 3052960043 while PLUTO keeps one.
- **`addrtype` (Geographic Identifier Type Code) — full enumeration `[DOC, padgui pp.9–12]`:**
  - **blank** = real Address range of a building ("by far the most common"; a single address = range where low==high; Low/High/B5SC/LGC/SideOfStreet/BIN populated).
  - **B** = NAUB (building with a BIN but no address/name; Low/High empty; multiple B rows if multiple frontages).
  - **F** = Vacant Street Frontage (no buildings, no pseudo-address; Low/High/BIN empty).
  - **G** = NAP of a complex ("a non-empty BIN identifies a designated 'principal' building of the complex").
  - **N** = NAP of a simplex.
  - **Q** = **Pseudo-Address Range** assigned to a vacant street frontage; **BIN empty**; guide: "Pseudo-addresses have no 'official' status and in particular are not likely to serve successfully as mailing addresses."
  - **R** = Real Street of a Vanity Address. **V** = Vanity Address (e.g. "1049 Fifth Ave" whose entrance is on E 86 St). **W** = Blank-Wall Building Frontage (façade, no entrance). **X** = NAP of a constituent entity of a complex.
- **RQ2 — "address of record" in PAD:** **PAD does not carry a single 'primary/address-of-record' flag per lot.** The closest ranking concept is `addrtype` = blank (real building address) vs Q (pseudo) vs the principal-building note under type G — none of which designates one address as "the" lot address. The authoritative single "address of record" is therefore **PLUTO.Address / DOF-PTS** (§6), not a PAD field.

### 4. LION Single Line Street Base Map — NOT an address→lot source (bounded negative, verified)
- `[LIVE]` LION FeatureServer layer 0 (`services5.arcgis.com/GfwWNkhOj9bNBqoJ/.../LION/FeatureServer/0?f=pjson`) = **polyline, 129 fields**. Address ranges are per-segment side: `FromLeft`,`ToLeft`,`FromRight`,`ToRight` (+ Queens hyphen forms `LLo_Hyphen`/`LHi_Hyphen`/`RLo_Hyphen`/`RHi_Hyphen`), keyed to `SegmentID`, `LBlockFaceID`/`RBlockFaceID`.
- **There is no BBL or tax-lot field** in the LION schema (only `LBoro`/`RBoro`, `BoroBndry`, blockface IDs, and `LATOMICPOLYGON`/`RATOMICPOLYGON` census building-blocks). **LION maps an address to a street segment/blockface, not to a tax lot.** It is a base layer Geosupport consumes (with PAD) — not usable standalone for address→BBL. `[LIVE]` (Corroborated `[DOC]` by padgui p.13: PAD `segid`/side-of-street are defined against the LION segment; "for address ranges not in LION, this field is blank.")

### 5. DOF Digital Tax Map (DTM) — the LOT-GEOMETRY target, keyed by BBL only
- `[LIVE]` `TAX_LOT_POLYGON` (Open Data `i38t-6if2`) — MultiPolygon, columns: `the_geom` (WGS84 lon/lat), `boro`, `block`, `lot`, `bbl` (text), `condo_flag`, `reuc_flag`, `air_lot_flag`, `sub_lot_flag`, `easement_flag`, `lot_note`, `effective_tax_year`, `bill_bbl_flag`, `nycmap_bldg_flag`, `conversion_exception_flag`, `value_reflected_out_flag`. **No address field.** Live row for the case:
  ```
  GET https://data.cityofnewyork.us/resource/i38t-6if2.json?$where=bbl='3052960043'
  → {"bbl":"3052960043","boro":"3","block":"5296","lot":"43","the_geom":{"type":"MultiPolygon",...},"bill_bbl_flag":"0","nycmap_bldg_flag":"1",...}
  ```
- **Cadence `[DOC]`:** extracted from DOF's internal system the last Friday monthly, refreshed on ArcGIS Online the 1st; DOF alternates Set A / Set B monthly. This is the authoritative DTM-lot polygon, reachable **only by BBL** — the address→BBL step (Geoclient/GeoSearch) must run first.

### 6. PLUTO / MapPLUTO — source of the displayable "address of record"
- `[LIVE + DOC]` `PLUTO`/`MapPLUTO` (Open Data `64uk-42ks`) field `address` = the DOF-PTS record address (§ root-cause). Note the Socrata number-typed `bbl` serializes with a `.00000000` tail (`"3052960043.00000000"`) — the existing `connectors/bbl.py` already strips this. To surface "which lot was analysed," store PLUTO.`address` (+ PLUTO `version`) alongside the resolved BBL.

---

## Live-case verification table — "1279 37 Street, Brooklyn" and BBL 3052960043

| Source | Request (keys omitted) | Result | Honestly links 1279 37 St → lot 43 / 3622 13 Ave? |
|---|---|---|---|
| **GeoSearch v2** `[LIVE]` | `GET geosearch.planninglabs.nyc/v2/search?text=1279 37 street brooklyn&size=3` | Feature 1 `"1279 37 STREET"` → `addendum.pad={"bbl":"3052960043","bin":"3340270","version":"26c"}`; Feature 2 `"1279 GARAGE 37 STREET"` → same bbl, `bin":"3123204"`; Feature 3 `"1279 EAST 37 STREET"` → different lot `3076370038` | **YES** — resolves to BBL 3052960043 (block 5296 lot 43) directly |
| GeoSearch, "th" variant `[LIVE]` | `...text=1279 37th street brooklyn` | `"1279 37 STREET"` → bbl 3052960043, bin 3340270 | YES (Pelias normalizes "37th"→"37") |
| GeoSearch, reverse `[LIVE]` | `...text=3622 13 avenue brooklyn` | `"3622 13 AVENUE"` → bbl 3052960043, bin **3340270** | YES — both frontages share the primary building BIN 3340270 |
| **MapPLUTO** `[LIVE]` | `64uk-42ks.json?$where=bbl='3052960043'` | `address="3622 13 AVENUE"` (only address; no "37 STREET") | Confirms the lot; **does NOT contain "1279 37 Street"** (root cause) |
| **DTM TAX_LOT_POLYGON** `[LIVE]` | `i38t-6if2.json?$where=bbl='3052960043'` | polygon returned, boro 3 / block 5296 / lot 43 | Lot geometry present; reachable only by BBL, no address in-record |
| **Geoclient v2** `[DOC — not run, key required]` | `GET api.nyc.gov/geoclient/v2/search?input=1279 37 street brooklyn` (or `/address?houseNumber=1279&street=37 street&borough=brooklyn`) | Expected: GRC 00/01, `bbl="3052960043"`, `buildingIdentificationNumber`, normalized address. High confidence (Function 1B uses the same PAD/SND data GeoSearch verified) but **not live-verified** | Expected YES — needs a keyed contract-test fixture to confirm |
| **LION** `[LIVE schema]` | n/a (no BBL field) | 129-field polyline, no tax-lot id | **NO** — cannot map address→lot standalone |

Failure-semantics probes `[LIVE]`: nonexistent street → wrong-street fallback features (bbls belong to other lots); out-of-range house number → different house numbers on the street; nonsense all return `match_type:"fallback"`, `confidence:0.8` — same values as the true hit.

---

## Recommendation (RQ5)

**Primary address→BBL:** **Geoclient v2** (`/v2/search`, fall back to `/v2/address`) — Geosupport Function 1B/BL is the official geocoder of record, handles corner/range/vanity addresses, returns BBL + BIN + normalized address + authoritative GRC status codes for clean no-match/ambiguity detection. Requires the free subscription key (owner action — Tier D credential, see §open questions).

**Cross-check / degraded-mode:** **GeoSearch v2** (keyless) — already live-verified on this exact case. Use it as the corroborating resolver and for autocomplete. Because it has no clean no-match, gate every result on `returned.housenumber == input.housenumber` AND normalized-street equality; record disagreement with Geoclient as a visible conflict (never silently pick one).

**Then, by the resolved BBL:** (a) fetch the **DTM lot polygon** from `TAX_LOT_POLYGON` (`i38t-6if2`) for the geometry actually analysed; (b) fetch **PLUTO.Address** (`64uk-42ks`) as the **"address of record"** to display "we analysed lot BBL 3052960043, address of record 3622 13 AVENUE, matched from your input 1279 37 Street."

**Provenance fields to store** (per resolution): `input_address_verbatim`; `resolver=geoclient|geosearch`; `matched_address_returned`; `bbl` (10-digit canonical) + raw; `bin`; for Geoclient `geosupportReturnCode`+`reasonCode`+`message` (1E and 1A) and `/v2/version` Geosupport release; for GeoSearch `addendum.pad.version` (e.g. 26c) + `match_type`/`confidence` (recorded, not trusted as the success test) + the housenumber/street equality check result; `address_of_record` = PLUTO.`address` + PLUTO `version`; `dtm_source` + `effective_tax_year` (+ DTM Set A/B if captured); WGS84 coordinates + CRS; `retrieved_at` UTC; `condoflag`/billing-BBL if the lot is a condo.

---

## Open questions / assumptions needing G1 data-contract review

1. **Geoclient live behavior for the case is not verified** — needs a keyed contract-test fixture (`/v2/search?input=1279 37 street brooklyn` → assert bbl 3052960043, bin, GRC 00/01). Key acquisition is an owner/Tier-D action.
2. **Geoclient rate limits/quota** — unpublished; visible only in the portal after sign-in. UNKNOWN.
3. **GeoSearch has no clean no-match** (verified). The success contract must be housenumber+street field-equality; `match_type`/`confidence` are non-discriminating (`fallback`/`0.8` even on the true hit). Confirm the normalization used to compare streets ("37 STREET" vs "37TH STREET", Queens hyphens).
4. **BIN selection when a lot has multiple BINs** — the case returned primary building `3340270` and garage `3123204` on one BBL. Need a documented rule for which BIN to surface (the record address's BIN vs all BINs).
5. **Pseudo-addresses (PAD `addrtype`=Q)** — an address→BBL match could land on a pseudo-address (no official status, BIN empty). Decide whether the connector accepts Q matches and how it flags them in the "which lot" display.
6. **Vanity addresses (`addrtype` V/R)** — Geosupport normalizes them; confirm the stored `matched_address_returned` records both the vanity input and the real street.
7. **Condo lots** — address→BBL may return a unit BBL or a billing BBL; PLUTO/DTM are keyed by the tax-lot BBL. The live case is NOT a condo (K4, `condoflag` unset), but the resolver must reconcile with the existing condo-resolver work (M5-T044) — G1 must define which BBL is analysed for condos.
8. **Freshness reconciliation** — GeoSearch PAD (`26c`) can lag Geoclient's server Geosupport release and DOF PTS (PLUTO). Store all three version stamps and surface staleness rather than hiding it. The `bc8t-ecyu` Open Data timestamp is frozen (2015) and must not be used as a freshness signal.
9. **PLUTO "address of record" is itself the low-number-of-range** per the dictionary — so for a range lot the displayed record address may be a range's low end, not a marketing address. Acceptable for "which lot was analysed," but document it.
10. **Context-file drift** — my worktree lacks the DB-026 row text and the current `geoclient_address.py`; confirm this research matches the current backlog row and connector before contracting.

---

## Sources (all retrieved 2026-09-18)

- Geoclient v2 (endpoints/GRC/auth): prior accepted research `docs/research/M0-T002-geoclient-address-resolution.md`; upstream https://mlipper.github.io/geoclient/ ; base URL https://api.nyc.gov/geoclient/v2
- GeoSearch v2 (live): https://geosearch.planninglabs.nyc/v2/search — docs https://geosearch.planninglabs.nyc/docs/
- PAD file layout: https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/padlayout.pdf
- PAD guide (addrtype codes, corner/frontage, pseudo/vanity): https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/padgui.pdf
- PAD on Open Data (file dataset): https://data.cityofnewyork.us/City-Government/Property-Address-Directory/bc8t-ecyu
- PLUTO Data Dictionary Aug 2026 (26v2), ADDRESS p.13: https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf
- MapPLUTO (live): https://data.cityofnewyork.us/resource/64uk-42ks.json
- DTM TAX_LOT_POLYGON (live): https://data.cityofnewyork.us/City-Government/TAX_LOT_POLYGON/i38t-6if2
- LION FeatureServer schema (live): https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/LION/FeatureServer/0 — LION landing https://www.nyc.gov/site/planning/data-maps/open-data/dwn-lion.page

---

**Requested status:** awaiting_gate. No repository files written; report returned as text for verbatim capture. Saved PDFs used for verbatim excerpts live under the session tool-results dir (PAD layout, PAD guide, PLUTO dict) if the orchestrator wants to re-verify quotes. One stable domain learning worth capturing (PAD-vs-PLUTO address-of-record mechanism + GeoSearch non-discriminating `match_type`/`confidence`) — flagged for the orchestrator rather than written to memory, per the read-only instruction.
