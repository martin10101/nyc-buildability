---
name: zoning-lot-lookup-semantics
description: How to resolve BBL + lot-level zoning from PLUTO/ZTLDB/nyzd, and the source-division traps (condo billing lots, bbox over-capture, address-string mismatch)
metadata:
  type: reference
---

Lot-level zoning resolution from the authoritative NYC sources (verified live 2026-09-18; PLUTO
channel version 26v2). Complements [[project_nyc-source-fetch-channels]].

**Endpoints:** PLUTO SODA `64uk-42ks`, ZTLDB SODA `fdkv-4t4z`
(`https://data.cityofnewyork.us/resource/<id>.json`); nyzd + MAPPLUTO ArcGIS layers at
`services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/{nyzd,MAPPLUTO}/FeatureServer/0`.

**Source division (load-bearing):**
- **ZTLDB `fdkv-4t4z` is the authoritative LOT-LEVEL zoning source** (10%/50% assignment rules).
  It carries `zoning_district_1..4` — ZD1 = greatest-area district; a ZD2 means a second district
  covers >=10% of the lot (i.e. a real split). Lot-level zoning lookups should key on ZTLDB.
- **ZTLDB OMITS condo BILLING lots (tax_lot 7501-7599) by design.** A billing-lot BBL returns
  `[]`. The condo's base land lot is a low-numbered DTM lot on the same block; mapping billing lot
  -> base land lot needs ACRIS/DOF (not derivable from the open SODA datasets). PLUTO *does* carry
  a condo aggregate record (keyed to the billing lot) but it is NOT the lot-level zoning source.
- **nyzd is explicitly "not intended for determining zoning at the individual tax lot level."** A
  nyzd envelope/bbox intersect **over-captures** adjacent districts for any large lot near a
  junction (a big lot's bbox touched M1-1, M1-2A/R7A, R5, R6 while the lot was authoritatively
  single R5). Use the lot **centroid** (MAPPLUTO `returnCentroid=true`) or a true polygon
  intersect, and trust ZTLDB over raw geometry. A geometry-vs-ZTLDB disagreement is a
  boundary-confidence/data-geometry case, NOT a genuine split.

**Field / query traps:**
- PLUTO `bbl` serializes as a float-string: `"3005250001.00000000"`. ZTLDB `bbl` is a clean
  string. SODA omits null fields per record (schema comes from the columns array, not record keys).
- PLUTO address format has NO ordinal suffix: `"1279 37 STREET"`, not `"1279 37th Street"`.
- **Range/corner addresses may have NO PLUTO record** and instead live under the lot's
  address-of-record on the CROSS street. E.g. "1279 37th Street, Bklyn" has no PLUTO row; the
  intended building is the corner lot whose PLUTO address is "3622 13 AVENUE" (BBL 3052960043).
  Resolve by enumerating the block (`$where=block=<n> AND borough='..'`) and matching built FAR
  (`bldgarea/lotarea`) / district to the known facts.
- **GeoSearch (`geosearch.planning.nyc.gov/v2/search`) returned EMPTY in this environment** (with
  and without a browser UA) — do not rely on it here; resolve identity via PLUTO/ZTLDB SODA + nyzd.
- `PLUTO.ResidFAR` corroborated the pinned-ruleset FAR exactly for flat R6-R12 districts, and
  returns the CONSERVATIVE value for wide-street-conditional districts (R7-1 3.44, R8 6.02) — but
  it is a city REFERENCE field, never the platform's calculated allowance (D-073-R006).

**Bash-tool guard in this isolated worktree:** shell `for`-loops and multi-`;` compound curl
commands are refused by the worktree-isolation guard ("too complex to verify it stays inside the
worktree"). Run each curl as its own plain command.
