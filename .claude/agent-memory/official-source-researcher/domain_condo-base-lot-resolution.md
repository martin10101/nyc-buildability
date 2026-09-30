---
name: domain-condo-base-lot-resolution
description: Official DOF DTM datasets that resolve a condo billing/unit BBL to its base land tax lot(s); fields, guarantees, failure modes
metadata:
  type: project
---

Condo billing BBLs (lot 7501+) and unit BBLs (lot 1001-6999) are absent from ZTLDB
(`fdkv-4t4z`) and never carry the base-lot linkage themselves. Resolve BEFORE any
zoning-lot lookup using DOF Digital Tax Map tabular SODA datasets (attribution
Department of Finance):

- **`p8u6-a6it` "Digital Tax Map: Condominiums"** — PRIMARY billing->base. Query
  `?condo_billing_bbl=<10-digit>`; returns ONE ROW PER BASE LOT (`condo_base_bbl`,
  `condo_base_boro/block/lot`, `condo_number`, `condo_key`, `condo_name`). Multi-lot
  condos return >1 row (verified: 3022647515 -> {3022640032, 3022640033}). BBL fields
  are TEXT (clean 10-digit strings, no PLUTO-style `.00000000`). 12,218 rows / 10,965
  distinct condos; 28 condos have NULL `condo_billing_bbl` (no billing lot assigned yet
  -> fall back to `condo_key`).
- **`eguu-7ie3` "Digital Tax Map: Condominium Units"** — reverse/unit path. Query
  `?unit_bbl=<unit BBL>`; maps to same `condo_base_bbl` + `unit_designation`, `floor_text`.
  307,614 rows. `?condo_key=<k>` gives the full unit set.
- **ArcGIS failover:** `services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/
  DTM_ETL_DAILY_view/FeatureServer`, tables `CONDO`(3)/`CONDO_UNIT`(4); also
  `TAX_LOT_POLYGON`(0), `AIR_LOT`/`SUB_LOT`/`REUC_LOT`, and `DAB_*` change-log
  (Digital Alteration Book). Returns identical mapping; condo fields come back as
  numbers (normalize).

**Why:** DB-002 / M5-T033 — billing BBL 3022647515 honestly returns no ZTLDB data;
resolving to base lots 32+33 (both R7-1, map 13B) unblocks the zoning lookup.

**How to apply:** billing/unit BBL -> DTM datasets -> SET of base lots -> run ZTLDB per
base lot. NEVER use PLUTO `appbbl` as the authoritative base set (single-valued; missed
lot 33 for this condo) — hint only. Geoclient gives billing BBL + unit-BBL RANGE
(normalization aid), NOT base land lots. ZoLa/MapPLUTO merge base lots into the
billing-lot geometry for DISPLAY only. If a multi-lot condo's base lots differ in zoning
district, that is a zoning-lot (ZR 12-10) legal-interpretation surface -> qualified human.
Full research + contract-test pack: `docs/research/condo-base-lot-resolution-sources.md`.
Related: [[nyc-source-fetch-channels]].
