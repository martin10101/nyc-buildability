# Wallabout records — 298 Wallabout Street, Brooklyn — recorded official data (B-08)

Pilot B, multi-lot / condominium case. Queue item **B-08** (Lane B; plan ID **M2-00**; directive
D-090, owner GO D-090-R015). Case: `docs/PRODUCT_PLAN_CURRENT_2026-09-28.md` section 11, and the
benchmark fixture `packages/contracts/fixtures/valid/benchmark_lot/wallabout_298_brooklyn_3022647515.json`.

Identity: borough **3**, block **2264**, condominium **1313**; base tax lots **32** and **33**;
condo billing lot **7515** (BBL 3022647515). Condo billing-to-base identity is already recorded in
`services/api/tests/connectors/test_dtm_condo_soda.py` and
`docs/research/condo-base-lot-resolution-sources.md` (sections 3.3, 4.3) — not re-captured here.
DTM tax-lot outlines (EPSG:4326, display-only) are already recorded in
`services/api/tests/fixtures/dtm_lot_outline/` (BBLs 32, 33, 7515).

- **Capture:** 14 official responses on **2026-10-02 UTC**. Python `urllib` GET, keyless, one request
  per file, sequential, at least 2.5 s apart. Each body is stored byte-for-byte as returned. No
  request needed a retry.
- **Provenance:** `MANIFEST.json` lists, for each file, the dataset id, source id, exact URL,
  `retrieved_at` (UTC), HTTP `Date` and `Last-Modified`, status (all 200), byte count and sha256.
- **Query shapes:** PLUTO, ZTLDB, MapPLUTO-geometry and DCM URLs come from each connector's own URL
  builder (`MANIFEST.json` field `connector`). DOB and ACRIS have no connector; their URLs follow the
  documented shape (field `documented_in`), with a `$select` that omits applicant / owner /
  filing-representative name columns.
- **Integrity:** `services/api/tests/connectors/test_benchmark_298_wallabout_fixtures.py` re-hashes
  every file and rebuilds every connector-backed URL. `.gitattributes` (`-text`) keeps the bytes
  exact.

## What the task asked for, and where it is

| B-08 item | File(s) | Finding |
|---|---|---|
| PLUTO billing row | `pluto_64uk-42ks_bbl_3022647515.json` | 1 row: `zonedist1` R7-1, `yearbuilt` 2005, `unitsres` 20, `unitstotal` 20, `lotarea` 5405, `bldgarea` 32289 (DOF building area — reference only), `version` 26v2, `condono` 1313 |
| PLUTO base lots (context) | `pluto_64uk-42ks_bbl_3022640032.json`, `..._33.json` | Both empty `[]`. Condo base lots carry no separate PLUTO record (plan section 4) |
| ZTLDB for lots 32 and 33 | `ztldb_fdkv-4t4z_bbl_3022640032.json`, `..._33.json` | Both `zoning_district_1` = **R7-1**. Billing lot 7515 (`ztldb_fdkv-4t4z_bbl_3022647515.json`) is empty `[]` — ZTLDB is keyed by base tax lots |
| Permits (DOB) | `dob_bis_jobs_ic3t-wcy2_bin_3388750.json`, `dob_now_jobs_w9ak-ipjd_bbl_3022647515.json`, `dob_now_co_pkdm-hqz6_bbl_3022647515.json`, `dob_bis_co_bs8b-p36w_bin_3388750.json` | BIN **3388750**. See below. Flag only; statuses/codes not interpreted |
| ACRIS (flag only) | `acris_legals_8h5j-fqxa_bbl_3-2264-32.json` (3 ids), `..._33.json` (38 ids) | Legals index metadata only. Documents not read, codes not interpreted, no zoning-lot claim |
| Street widths | `dcm_street_centerline_lot_envelope_3022647515.json` (+ `mappluto_lot_3022647515_epsg2263.json`) | See below. Per-frontage assignment is B-03/B-04; one-sided bounds stay UNRESOLVED (D-052) |
| DTM | (already recorded in `services/api/tests/fixtures/dtm_lot_outline/`) | Referenced, not re-captured |

## Data versions at capture

| Source | Version / freshness recorded |
|---|---|
| PLUTO `64uk-42ks` | billing row `version` = **26v2** |
| MapPLUTO (DCP_GIS `MAPPLUTO`) | billing feature `Version` = **26v2** |
| ZTLDB `fdkv-4t4z`, DCM, DOB, ACRIS | HTTP `Last-Modified` per file in `MANIFEST.json` |

## Comparison with plan section 11 (Pilot B)

Verdicts: **agrees**, **differs** (with the numbers), or **not recorded** (with the reason).

| Plan section 11 statement | Recorded (file → field) | Verdict |
|---|---|---|
| Zoning district R7-1 | PLUTO billing `zonedist1` "R7-1"; ZTLDB base lots 32 and 33 `zoning_district_1` "R7-1" | **agrees** — now backed by official records (was `pending` in the benchmark fixture) |
| Rezoned from M1-2 in 2001 (C 000109 ZMK) | No city dataset here states the map-amendment number | **not recorded:** CPC application numbers are not in PLUTO/ZTLDB; stays a plan fact |
| 7-story building from 2005 | PLUTO `yearbuilt` "2005"; DOB BIS NB 301396567 `proposed_no_of_stories` "7" (signed off 2006-08-23) | **agrees** |
| 20-unit building | PLUTO `unitsres` / `unitstotal` "20" | **agrees with PLUTO**, but DOB NB 301396567 `proposed_dwelling_units` = **14** (disagreement 1) |
| 2023 stop-work order for an unpermitted extra floor | Not in the DOB job datasets or either CO dataset; no stop-work-order dataset is registered | **not recorded — Check needed:** no connector/source for DOB stop-work orders. The DOB NOW bulkhead/rooftop-access alterations (below) are flagged, not interpreted as the order |
| Street widths unconfirmed | DCM segments recorded (below); per-frontage width needs geometry | **not resolved by design:** "Needs street width" per frontage (disagreement 2) |
| Lot 33 as a base lot (unconfirmed) | ZTLDB returns a record for base lot 33 (R7-1); the recorded DTM condo response already lists 32 and 33 as base lots of condo 1313 | **corroborated that lot 33 is a base tax lot.** No combined zoning-lot claim is made |

## DOB permits (flag only)

- **BIN 3388750.** DOB BIS NB **301396567** (filed under lot 32; pre-filing 2002-08-20; **signed off
  2006-08-23**): 7 stories, 14 proposed dwelling units, `total_construction_floor_area` 32,000.
  Related BIS A1 310303230 ("parking space and curb cut", permit issued) shows `proposed_zoning_sqft`
  28,000; A2 310233137 (parking, plan-exam disapproved); A2 301494791 (signed off). The NB row is
  **duplicated** in the response (dedupe before counting, as in the 215-16 Northern pack).
- **DOB NOW Build** on billing lot 7515 (BIN 3388750): B01034323-I1 (Approved) and B00985568-I1
  (Withdrawn) — "framed bulkhead with rooftop access"; B00959864-I1 — sidewalk shed (LOC Issued).
- **Certificate of occupancy:** DOB NOW CO (`pkdm-hqz6`) and DOB BIS CO (`bs8b-p36w`) both return
  `[]` for this BIN / billing BBL. No CO row is recorded. The NB sign-off date (2006-08-23) is the
  closest recorded milestone; it is not a CO.

## Street widths (DCM centerlines in the billing-lot envelope)

The billing lot is the only MapPLUTO polygon for the site (EPSG:2263; base lots 32/33 have none).
The envelope is the polygon's bounding box padded 100 ft (the wide-street buffer). Centerlines that
intersect it:

| OBJECTID | Street_NM | Streetwidth | Note |
|---|---|---|---|
| 49245, 52049 | Wallabout Street | **70** | < 75 → narrow (1961 default) |
| 42403, 42404, 42405 | Wallabout Street | **>75** | one-sided bound → **UNRESOLVED** (D-052); never auto-wide |
| 41073 | Marcy Avenue | **70** | < 75 → narrow |
| 11306 | Marcy Avenue | **>75** | one-sided bound → **UNRESOLVED** (D-052) |
| 50973 | Union Avenue | **80** | = / > 75 → wide |
| 43945 | Union Avenue | **>80** | one-sided bound → **UNRESOLVED** (D-052) |

`Streetwidth` is a free-text mapped-width field (no official field-level spec). Which segment abuts
which frontage — and therefore the per-frontage width — is a geometry result owned by B-03/B-04
(site geometry and per-frontage street width); it is **not** assigned here. No frontage is given a
silent narrow default (plan section 4; D-051).

## Disagreements and new facts (logged, not resolved)

1. **Dwelling units: 14 vs 20.** DOB BIS NB 301396567 states 14 proposed dwelling units; PLUTO
   `unitsres`/`unitstotal` and plan section 11 say 20. Recorded both; not reconciled (flag only).
   The condo has 20 recorded unit lots total across lots 32 (14) and 33 (6) per the DTM condo-unit
   record — the "14" coincidence with lot 32's unit-lot count is noted, not interpreted.
2. **Street-width assignment.** Wallabout Street carries both "70" and ">75" segments near the lot;
   Marcy Avenue "70"/">75"; Union Avenue "80"/">80". A single frontage width needs the geometry path.
3. **Existing zoning floor area is not established here (B-05 owns it).** The DOB NB carries 32,000
   sq ft construction floor area and `proposed_zoning_sqft` 0; the A1 carries 28,000; PLUTO
   `bldgarea` 32,289 is DOF building area and must never be used as zoning floor area.

## Not recorded (no connector or registered source)

- DOB stop-work orders (no dataset connector/source registered) → the 2023 order stays Check needed.
- The 2001 CPC map amendment (C 000109 ZMK).
- ACRIS document images, the ACRIS document-code list, and the ACRIS Real Property Master rows
  (the Legals index is the flag; the documents are not read).
- FEMA flood zone, E-designation, LPC landmarks, transit zone (not in B-08 scope).
