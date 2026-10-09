# Condo billing BBL -> base/land tax lot resolution — official-source research

- **Task:** DISCOVERY_BACKLOG DB-002 (research only; no ledger task, no production code, no git/gh/project_control.py).
- **Producer agent:** official-source-researcher
- **Retrieval date for all live queries below:** 2026-09-18 (unless a prior report is cited).
- **Question answered:** Which official NYC sources deterministically resolve a condo billing BBL (lot 7501+) to its base/land tax lot(s), with what fields, guarantees, and failure modes — so a `condo -> base-lot` step can run BEFORE the zoning-lot lookup.
- **Canonical worked example:** BBL **3022647515** (Brooklyn, block 2264, billing lot 7515), condo no. 1313, "298 WALLABOUT STREET" per PLUTO, 20 units. This is the M5-T033 / DB-002 case that honestly returns no ZTLDB data today.
- **Discipline:** Every load-bearing claim carries an official-source URL + retrieval date. Raw responses are embedded verbatim (trimmed only where noted). Nothing about legal *effect* (zoning lot identity) is asserted — that boundary is flagged for a qualified human.

---

## 1. Top-line recommendation

**Primary resolver — DOF Digital Tax Map "Condominiums" table on NYC Open Data, Socrata dataset `p8u6-a6it`.** It maps `condo_billing_bbl` (the 7501+ billing lot) directly to one row **per base land lot**, giving `condo_base_bbl` / `condo_base_boro` / `condo_base_block` / `condo_base_lot`, plus `condo_number` / `condo_key`. It is authoritative (attributed to the Department of Finance, the owner of tax-lot identity in the DTM), tabular/SODA-queryable per-BBL (no bulk download — thin-client safe), and returns **all** base lots for multi-lot condos.

**Reverse / unit-BBL resolver — DOF Digital Tax Map "Condominium Units" table, Socrata dataset `eguu-7ie3`.** It maps an individual condo **unit** BBL (the 1001–6999 series) to the same `condo_base_bbl`, plus `unit_designation` and `floor_text`. Use it when the user enters a unit BBL rather than the billing BBL.

**Verified secondary channel — the DOF DTM ArcGIS feature server** `services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer`, tables `CONDO` (id 3) and `CONDO_UNIT` (id 4). It returned the identical base-lot mapping and is the failover if the Socrata endpoint is unavailable.

**End-to-end proof (loop closed 2026-09-18):** ZTLDB (`fdkv-4t4z`) returns `[]` for billing BBL 3022647515 but returns **R7-1 / zoning map 13B** for BOTH resolved base lots 3022640032 and 3022640033 — so the resolution step converts today's honest-no-data into a real zoning-lot lookup. Confidence is **HIGH** for the primary path (directly verified with raw official responses and loop-closed against the downstream ZTLDB) and **MEDIUM** on cadence reconciliation and rarer edge cases (air/sub/REUC-lot condos, base-lot reuse, and the legal handling of condos whose base lots straddle two zoning lots).

---

## 2. Candidate sources evaluated

| # | Source | Identity | Role | Verdict |
|---|---|---|---|---|
| A | DOF DTM **Condominiums** (Socrata) | `p8u6-a6it` (tabular SODA) | billing BBL -> base lot(s) | **PRIMARY** |
| B | DOF DTM **Condominium Units** (Socrata) | `eguu-7ie3` (tabular SODA) | unit BBL -> base lot | **PRIMARY (reverse/unit path)** |
| C | DOF DTM **ArcGIS** feature server | `DTM_ETL_DAILY_view` FeatureServer, tables CONDO(3)/CONDO_UNIT(4) | same data, geospatial + tabular | **VERIFIED SECONDARY / failover** |
| D | **PLUTO** `appbbl` / `condono` | Socrata `64uk-42ks` (DCP) | corroborating hint only | **NOT authoritative for base-lot set — single-valued, incomplete for multi-lot condos** |
| E | **Geoclient / Geosupport** | hosted API | identity normalization (address->BBL, unit->billing, unit-BBL range) | **DISCOVERY/NORMALIZATION AID ONLY — cannot yield base land lots** |
| F | **ZoLa** (DCP zoning map) | zola.planning.nyc.gov (built on MapPLUTO) | how the city presents condos | **Not a data API; merges base lots into the billing-lot geometry for display** |
| G | DOF DTM main entry | Socrata `smk3-tmxj`; also `eguu-7ie3` collection | catalog/collection pointer | pointer to the collection above |

---

## 3. PRIMARY — DOF DTM "Condominiums" (`p8u6-a6it`)

### 3.1 Identity, attribution, cadence, freshness (metadata fetch)

- Metadata: `https://data.cityofnewyork.us/api/views/p8u6-a6it.json` (retrieved 2026-09-18).
- Name: **"Digital Tax Map: Condominiums"**; id `p8u6-a6it`; **attribution "Department of Finance (DOF)"**; `viewType: tabular` / `displayType: table` (i.e. a live SODA resource, not an href blob).
- Timestamps (raw -> ISO): `rowsUpdatedAt` 1788271556 = **2026-09-01T14:05:56Z**; `createdAt` 1734102769 = 2024-12-13T15:12:49Z; `publicationDate` 1769016506 = 2026-01-21T17:28:26Z. Freshness signal for a connector = `rowsUpdatedAt` (17 days old at retrieval).
- Cadence fields (`metadata.custom_fields.Update`): `Update Frequency: "Weekly"`, `Data Change Frequency: "Daily"`, with detail: *"DOF Tax Map Unit (TMU) makes daily edits to the Tax Map that can be observed on DOF's Property Information Portal."*
- Description cadence (verbatim, differs from the field above — see §8 OQ-1): *"Data is extracted from DOF's internal system on the last Friday of each month and refreshed on ArcGIS Online on the 1st. The online map always shows the most recent version."*
- Reliability note (verbatim, from the sibling `eguu-7ie3` description): *"To ensure reliability, the Tax Map alternates between Set A and Set B each month. If one set has issues, the previous month's copy remains online."*
- Change log (verbatim): *"Digital Alteration Book (DAB): The DAB is the official log of map changes — such as new lots, merges, or boundary shifts … available through the Property Information Portal."* — the authoritative provenance channel for *why/when* a condo's lot structure changed.
- Disclaimer (verbatim): *"This dataset reflects formal applications submitted to DOF but may not reflect the latest changes in other City systems … provided for informational purposes only and is not guaranteed to be accurate as of today's date."*

### 3.2 Schema (9 columns; from the `columns` array, verbatim field names + official descriptions)

| SODA field | Type | Official description (trimmed) |
|---|---|---|
| `condo_base_boro` | text | one-digit borough of the base feature |
| `condo_base_block` | number | five-digit block of the base feature |
| `condo_base_lot` | number | four-digit lot of the base feature |
| `condo_base_bbl` | **text** | Boro-Block-Lot concatenation of the base lot |
| `condo_base_bbl_key` | text | concatenation of `condo_base_bbl` + condo boro + condo number |
| `condo_key` | number | concatenation of Condo Boro + Condo Number in 6-digit format |
| `condo_number` | number | unique id per condominium, assigned at creation, separated by boro |
| `condo_name` | text | condominium name (nullable — null on the worked example) |
| `condo_billing_bbl` | **text** | *"the concatenation of the billing lot's (series 7501, 7502, 7503, etc.) borough, block, and lot. Each record can only have a single Billing lot"* |

**Guarantee that matters for the connector:** the BBL fields are Socrata **text** type, so they come back as clean zero-padded 10-digit strings (`"3022640032"`). This avoids the PLUTO trap where `bbl` is a *number* type and serializes as `"3022647515.00000000"` (see `docs/research/pluto-mappluto-2026-07-16.md` fixture F12). No decimal normalization needed here; still validate the `^\d{10}$` shape.

### 3.3 Raw response — billing BBL 3022647515 (the DB-002 case)

Request: `https://data.cityofnewyork.us/resource/p8u6-a6it.json?condo_billing_bbl=3022647515` (HTTP 200, retrieved 2026-09-18):

```json
[{"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"32","condo_base_bbl":"3022640032","condo_base_bbl_key":"3022640032301313","condo_key":"301313","condo_number":"1313","condo_billing_bbl":"3022647515"},
 {"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"33","condo_base_bbl":"3022640033","condo_base_bbl_key":"3022640033301313","condo_key":"301313","condo_number":"1313","condo_billing_bbl":"3022647515"}]
```

**This is a multi-lot condo:** billing lot 7515 (condo 1313) resolves to **two** base land lots — `3022640032` (lot 32) and `3022640033` (lot 33). A resolver MUST return the *set* of base lots, never assume one.

### 3.4 Population and failure-mode measurements (live counts, 2026-09-18)

- `?$select=count(condo_key)` -> **12,218** rows.
- `?$select=count(distinct condo_key)` -> **10,965** distinct condos. The 1,253-row surplus is multi-base-lot condos (each contributes >1 row) — multi-lot condos are common, not exotic.
- `?$select=count(condo_key)&$where=condo_billing_bbl IS NULL` -> **28** condos with **NO billing BBL** (DOF has not yet assigned a billing lot). These cannot be reached by the billing-BBL path; see §7 fallback.
- No-match behavior is deterministic: `?condo_billing_bbl=3022647599` (nonexistent) -> `[]`; `?condo_billing_bbl=3022640032` (a normal land lot, not a billing lot) -> `[]`.

---

## 4. PRIMARY (reverse) — DOF DTM "Condominium Units" (`eguu-7ie3`)

### 4.1 Identity & schema

- Metadata: `https://data.cityofnewyork.us/api/views/eguu-7ie3.json` (retrieved 2026-09-18). Name **"Digital Tax Map: Condominium Units"**; attribution **DOF**; `viewType: tabular`. `rowsUpdatedAt` 1788271541 = **2026-09-01T14:05:41Z** (same release moment as `p8u6-a6it`). Total rows `?$select=count(unit_bbl)` -> **307,614**.
- 16 columns: `condo_base_boro/block/lot/bbl`, `condo_number`, `condo_key`, `condo_base_bbl_key` (same base-lot linkage as the Condominiums table) **plus the unit side**: `unit_boro`, `unit_block`, `unit_lot`, `unit_bbl` (text), `unit_designation` (e.g. `"1A"`), `floor_text` (which floor(s) the unit occupies), `model`, `geometry_type`, `effective_tax_year`.

### 4.2 Raw response — reverse lookup of a unit BBL

Request: `https://data.cityofnewyork.us/resource/eguu-7ie3.json?unit_bbl=3022642601` (retrieved 2026-09-18):

```json
[{"condo_base_boro":"3","condo_base_block":"2264","condo_base_lot":"32","condo_base_bbl":"3022640032","condo_number":"1313","condo_key":"301313","condo_base_bbl_key":"3022640032301313","unit_boro":"3","unit_block":"2264","unit_lot":"2601","unit_bbl":"3022642601","unit_designation":"1A","model":"T","geometry_type":"Table"}]
```

So a user-entered unit BBL `3022642601` (unit "1A", in the 1001–6999 unit series) resolves straight to base lot `3022640032`.

### 4.3 Cross-check that ties the two tables together

- `?condo_key=301313&$select=count(unit_bbl)` -> **20** units — exactly PLUTO's `unitstotal`/`unitsres` = 20 for the billing lot, a strong internal-consistency signal.
- `?condo_key=301313&$select=condo_base_bbl,count(unit_bbl)&$group=condo_base_bbl` ->
  ```json
  [{"condo_base_bbl":"3022640032","count_unit_bbl":"14"},
   {"condo_base_bbl":"3022640033","count_unit_bbl":"6"}]
  ```
  The 20 units genuinely split across the two base lots (14 on lot 32, 6 on lot 33) — confirming the multi-lot structure from the units side, independently of the Condominiums table.

---

## 5. VERIFIED SECONDARY — DOF DTM ArcGIS feature server (failover)

- Endpoint root: `https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer` (org key `yG5s3afENB5iO9fj`; referenced as the "Individual layers … Digital Tax Map Feature Server" download in both Socrata dataset descriptions).
- `?f=pjson` layer/table inventory (retrieved 2026-09-18): layers `TAX_LOT_POLYGON`(0), `TAX_BLOCK_POLYGON`(1); tables `AIR_LOT`(2), **`CONDO`(3)**, **`CONDO_UNIT`(4)**, `REUC_LOT`(5), `SUB_LOT`(6), map-library + **DAB_*** change-log tables (9–17), `PTS_DESC_DAILY`(18), `PTS_CONDO_DAILY`(19). `serviceDescription`/`copyrightText` were empty (see §8 OQ-2 for the residual org-name confirmation).
- Query proof — `.../FeatureServer/3/query?where=CONDO_BILLING_BBL='3022647515'&outFields=CONDO_BASE_BBL,CONDO_BILLING_BBL,CONDO_NUMBER,CONDO_KEY,CONDO_NAME&returnGeometry=false&f=json` returned the **same two base lots** (`3022640032`, `3022640033`, condo 1313, `CONDO_NAME: null`). Note ArcGIS types `CONDO_NUMBER`/`CONDO_KEY` as numbers (1313 / 301313) whereas Socrata returns them as strings — normalize on ingest.
- Role: use only as failover for the Socrata endpoint, or when the polygon geometry (`TAX_LOT_POLYGON`, EPSG per the DTM service) or the DAB change log is needed. `AIR_LOT`/`SUB_LOT`/`REUC_LOT` tables exist here and are relevant to the air-lot / sub-lot condo edge cases (§8 OQ-3).

---

## 6. Sources that must NOT carry the base-lot decision

### 6.1 PLUTO `appbbl` / `condono` — corroborating hint only

- Live PLUTO record for the billing BBL (`https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3022647515`, retrieved 2026-09-18, **version 26v2**) includes: `condono: "1313"`, `appbbl: "3022640032.00000000"`, `appdate: "2006-07-06T00:00:00.000"`, `zonedist1: "R7-1"`, `unitstotal: "20"`.
- **`appbbl` (Apportionment BBL) returned ONLY lot 32** — it missed lot 33. PLUTO's `appbbl` is single-valued (the pre-apportionment predecessor lot) and therefore **structurally incomplete for multi-lot condos**. It also carries the number-type trailing-decimal serialization. Treat `appbbl` as a cross-check/hint that should *agree with one of* the DTM base lots, never as the authoritative base-lot set. `condono` is useful to join to the DTM `condo_number` (per-borough) but is not itself the base-lot linkage.
- Provenance for PLUTO field meanings: PLUTO data dictionary (26v-series) at `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf`; condo/billing-BBL semantics in `docs/research/pluto-mappluto-2026-07-16.md` §4.4.

### 6.2 Geoclient / Geosupport — normalization aid, not a base-lot source

- Geoclient `/v2/bbl` and `/v2/bin` return `condominiumBillingBbl`, `lowBblOfThisBuildingsCondominiumUnits`, `highBblOfThisBuildingsCondominiumUnits` (see `docs/research/M0-T002-geoclient-address-resolution.md` §2.6). These normalize user input: address/unit-BBL/BIN -> billing BBL, and give the **unit-BBL range (1001–6999 series)**.
- **What it may be used for:** discovery/normalization only — e.g. turning a messy address or a unit BBL into the billing BBL that then feeds the DTM lookup, or validating that an input BBL is a condo. **What it may NOT be used for:** yielding the base LAND lot(s). Its low/high range is *unit* lots, not base lots, so it cannot substitute for `p8u6-a6it`. Separately, Geoclient/Geosupport is already **KILLED for legal street-width use in this repo** (paved-width semantics; PROGRAM_KNOWLEDGE / D-052) — that kill is about width, but the same "official identity resolver, not a legal-measurement source" posture applies: identity hint yes, load-bearing base-lot or zoning fact no.

### 6.3 ZoLa — shows the city's convention, not an ingestible relationship

- ZoLa (`https://zola.planning.nyc.gov/`, source `github.com/NYCPlanning/labs-zola`, data page `https://zola.planning.nyc.gov/data`) is built on **MapPLUTO**. In MapPLUTO the condo **billing lot (7501+) carries the merged geometry of its base lots** (the base-lot "FKA" merge behavior verified in `docs/research/pluto-mappluto-2026-07-16.md` §2.4). So ZoLa resolves a condo by *displaying the billing lot as one merged polygon with its zoning* — it does not expose a billing->base step to the user because the merge is pre-baked into display geometry. Consequence: ZoLa's approach is a **display convenience only** (MapPLUTO geometry is 4326/display-grade and explicitly not for measurement); it is not a substitute for the DTM base-lot relationships when you need per-base-lot zoning assignment and measurement. The DTM tables (§3–§5) are the ingestible, per-base-lot source of truth.

---

## 7. Recommended resolution path (deterministic algorithm)

Given a user-entered BBL `X` (already normalized to 10-digit string via Geoclient/Geosupport if needed):

1. **Classify the lot from the lot number** (chars 6–9 of the BBL):
   - `7501–7599` -> billing lot -> step 2.
   - `1001–6999` -> condo unit lot -> step 3.
   - else -> not a condo BBL; go straight to the normal zoning-lot lookup (no resolution needed).
2. **Billing lot:** query `p8u6-a6it?condo_billing_bbl=X`. Collect every row's `condo_base_bbl` into a set `B`. If `[]`, apply the fallbacks in step 4.
3. **Unit lot:** query `eguu-7ie3?unit_bbl=X`. Take `condo_base_bbl` (and optionally `condo_key`, then expand to all base lots via `p8u6-a6it?condo_key=<k>`). Collect into `B`.
4. **Fallbacks (in order), each with recorded provenance and a downgraded confidence tag:**
   a. Query `p8u6-a6it?condo_key=<k>` when a `condo_key`/`condo_number` is known but the billing BBL is null/absent (covers the 28 no-billing-BBL condos).
   b. Cross-check PLUTO `appbbl` for the billing BBL — it should equal one member of `B`; if `B` is empty, `appbbl` is a *single-lot hint only*, flagged low-confidence.
   c. If still unresolved, emit an honest `condo_base_lot_unresolved` state (do NOT fabricate a base lot).
5. **Downstream zoning lookup:** run the existing ZTLDB / zoning-features pipeline for **each** base lot in `B`. Store the full set with provenance (dataset id, `rowsUpdatedAt`, retrieval time, `condo_number`).
6. **Divergence handling (legal boundary):** if the base lots in `B` carry **different** zoning districts/overlays, the condo may span more than one zoning lot — surface all of them and **do not auto-collapse to one zoning determination**; a zoning lot (ZR §12-10) is a legal construct distinct from a tax lot, so this is a qualified-human interpretation surface, not a deterministic merge.

**Worked proof of step 5 (retrieved 2026-09-18):** ZTLDB `fdkv-4t4z` -> billing `3022647515` = `[]`; base `3022640032` = `{zoning_district_1:"R7-1", zoning_map_number:"13B"}`; base `3022640033` = `{zoning_district_1:"R7-1", zoning_map_number:"13B"}`. Both base lots agree (R7-1) here, so the zoning lot is consistent for condo 1313 — but the algorithm must still handle the general divergent case. This also documents a real discrepancy: the **ZTLDB data dictionary claims "For condominiums, the BBL is for the billing lot," yet ZTLDB is empirically keyed by the base/DTM lots and does not contain the billing lot 7515** — reinforcing that the resolution step is mandatory, and the dictionary sentence should not be trusted for condos.

---

## 8. Edge cases and limitations

1. **Multi-lot condo (verified):** one billing BBL -> N base lots (`3022647515` -> {32,33}). Always handle a set. ~1,253 of 12,218 rows come from such condos.
2. **Condo spanning zoning lots:** base lots may sit in different zoning districts; downstream must present all and defer the legal zoning-lot determination to a qualified human (§7 step 6).
3. **Condo with no billing BBL (28 condos):** `condo_billing_bbl` is NULL; billing-BBL path returns `[]`. Fall back to `condo_key`/`condo_number` (step 4a) or the units table.
4. **Unit-BBL entry (1001–6999):** handled by `eguu-7ie3` (§4).
5. **PLUTO `appbbl` incompleteness:** single-valued; misses secondary base lots of multi-lot condos — never authoritative.
6. **Air lots / sub lots / REUC lots:** the DTM exposes `AIR_LOT`(2), `SUB_LOT`(6), `REUC_LOT`(5) tables; condos can involve air lots. Whether such condos appear cleanly in `p8u6-a6it` with a land base lot is not fully characterized here (OQ-3).
7. **Set A / Set B monthly alternation:** the published data swaps between two sets for reliability; a connector may see content shift at the monthly boundary and should pin `rowsUpdatedAt` per ingestion.
8. **Cadence ambiguity:** `custom_fields` says Weekly/Daily; the description says monthly extract refreshed on the 1st; the ArcGIS view is named `DTM_ETL_DAILY_view`. Use `rowsUpdatedAt` as the ground-truth freshness signal, not the prose cadence (OQ-1).
9. **Auth/limits:** standard Socrata SODA — send an `X-App-Token` header (tokenless requests share a throttled IP pool and can return HTTP 429; see `docs/research/pluto-mappluto-2026-07-16.md` E7 / `https://dev.socrata.com/docs/app-tokens`). ArcGIS `maxRecordCount`/pagination for the DTM service was not measured (OQ-4).
10. **Not the City Map:** the DTM is DOF's tax map for billing/assessment; it is authoritative for **tax-lot identity and condo structure**, which is exactly what this step needs, but zoning/legal-lot conclusions still come from the zoning pipeline + human review.

### Open questions (OQ)

- **OQ-1** Reconcile the three stated cadences (Weekly field vs monthly-extract prose vs daily ETL view). Requires DOF confirmation; use `rowsUpdatedAt` meanwhile.
- **OQ-2** Confirm the ArcGIS org `yG5s3afENB5iO9fj` is DOF by name (service copyright was empty; provenance currently rests on the Socrata datasets' own download links pointing at this server).
- **OQ-3** Characterize air-lot / sub-lot / REUC-lot condos: do they resolve to a normal land base lot in `p8u6-a6it`, and how should measurement treat air lots?
- **OQ-4** ArcGIS `maxRecordCount` and pagination for `CONDO`/`CONDO_UNIT`; and the exact Socrata page/limit defaults for these two datasets.
- **OQ-5** Is `condo_billing_bbl` globally unique (one condo per billing BBL)? Observed 1:1 here; not proven citywide.
- **OQ-6** Can one base lot belong to more than one condo (base-lot reuse across condo_keys)? Not observed; not disproven.
- **OQ-7** `effective_tax_year` semantics on the units table, and whether historical/retired unit rows appear.
- **OQ-8** Set A vs Set B: which set the Socrata endpoint serves at a given time, and the exact Set A/Set B download URLs (truncated in the description).

---

## 9. Proposed contract-test pack (for a future `dtm-condo-resolver` connector)

All fixtures are small raw responses stored with request URL (token stripped) and retrieval timestamp; KB-scale, thin-client safe. Pin against the two Socrata datasets, with the ArcGIS query as the failover fixture.

| # | Fixture | Request | Assertion |
|---|---|---|---|
| C1 | multi-lot billing resolve | `p8u6-a6it?condo_billing_bbl=3022647515` | 2 rows; base BBLs == {`3022640032`,`3022640033`}; both `condo_key`=`301313` |
| C2 | unit reverse resolve | `eguu-7ie3?unit_bbl=3022642601` | 1 row; `condo_base_bbl`=`3022640032`; `unit_designation`=`1A` |
| C3 | unit set consistency | `eguu-7ie3?condo_key=301313&$select=condo_base_bbl,count(unit_bbl)&$group=condo_base_bbl` | {32:14, 33:6}; total 20 |
| C4 | no-match (nonexistent billing) | `p8u6-a6it?condo_billing_bbl=3022647599` | `[]` |
| C5 | no-match (land lot as billing) | `p8u6-a6it?condo_billing_bbl=3022640032` | `[]` |
| C6 | null-billing fallback | `p8u6-a6it?condo_key=<a NULL-billing condo>` | rows returned via condo_key though billing path is empty |
| C7 | BBL string shape | any row | `condo_base_bbl`/`condo_billing_bbl` match `^\d{10}$` (text, no trailing `.0000`) |
| C8 | loop closure to ZTLDB | `fdkv-4t4z?bbl=3022640032` and `=3022640033` | both `R7-1`, map `13B`; `fdkv-4t4z?bbl=3022647515` == `[]` |
| C9 | PLUTO appbbl incompleteness guard | `64uk-42ks?bbl=3022647515` | `appbbl`=`3022640032` only -> assert resolver does NOT rely on appbbl for the base-lot set |
| C10 | schema drift | `/api/views/p8u6-a6it.json` columns snapshot (9 cols) and `eguu-7ie3` (16 cols) | column-list diff vs stored contract |
| C11 | freshness | `/api/views/p8u6-a6it.json` `rowsUpdatedAt` | recorded per ingestion; alert if age exceeds threshold |
| C12 | rate-limit shape | tokenless burst (isolated test only) | HTTP 429 shape captured |
| C13 | ArcGIS failover parity | `DTM_ETL_DAILY_view/FeatureServer/3/query?where=CONDO_BILLING_BBL='3022647515'&outFields=*&f=json` | same 2 base lots; note number-typed condo fields |
| C14 | divergent-zoning surfacing | a multi-lot condo whose base lots differ in `zoning_district_1` (to be found) | resolver returns all zoning results, no auto-collapse |

---

## 10. Source register (all live queries retrieved 2026-09-18 unless noted)

| Ref | Official URL | Used for |
|---|---|---|
| S1 | `https://data.cityofnewyork.us/api/views/p8u6-a6it.json` | Condominiums dataset identity, DOF attribution, 9-col schema, cadence, timestamps |
| S2 | `https://data.cityofnewyork.us/resource/p8u6-a6it.json?condo_billing_bbl=3022647515` | primary billing->base raw response (2 base lots) |
| S3 | `https://data.cityofnewyork.us/resource/p8u6-a6it.json?$select=count(condo_key)` / `count(distinct condo_key)` / `$where=condo_billing_bbl IS NULL` | population + null-billing counts (12,218 / 10,965 / 28) |
| S4 | `https://data.cityofnewyork.us/api/views/eguu-7ie3.json` | Condominium Units identity, 16-col schema, cadence, Set A/B + DAB + disclaimer prose |
| S5 | `https://data.cityofnewyork.us/resource/eguu-7ie3.json?unit_bbl=3022642601` / `?condo_key=301313&...` | unit reverse resolve + 20-unit split (14/6) |
| S6 | `https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer?f=pjson` and `/3/query?...` | ArcGIS failover: table inventory + parity query |
| S7 | `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3022647515` | PLUTO 26v2 record: `condono`, `appbbl`(=32 only), `appdate`, `unitstotal`=20 |
| S8 | `https://data.cityofnewyork.us/resource/fdkv-4t4z.json?bbl=3022647515` / `=3022640032` / `=3022640033` | loop closure: billing `[]`, both base lots R7-1/13B |
| S9 | `https://zola.planning.nyc.gov/` ; `https://github.com/NYCPlanning/labs-zola` ; `https://zola.planning.nyc.gov/data` | ZoLa is MapPLUTO-based; billing-lot merged-geometry display convention |
| S10 | `docs/research/pluto-mappluto-2026-07-16.md`; `docs/research/M0-T002-geoclient-address-resolution.md`; `docs/research/zoning-features-ztldb-2026-07-16.md` | prior verified findings (PLUTO condo/appbbl, Geoclient condo fields, ZTLDB schema/dictionary) |

---

## 11. Blockers

None for this research. Two forward flags (not blockers): (a) the **connector build** is a separate future ledger task — this is research only; (b) the **condo-spanning-zoning-lots** case (§7 step 6) is a legal-interpretation surface that must route to a qualified human, not be auto-resolved by deterministic code.
