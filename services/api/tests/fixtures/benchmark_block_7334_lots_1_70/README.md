# Block 7334, Queens, tax lots 1 and 70 — recorded official data (B-07)

Tax lot **1** (BBL 4073340001, 215-10 Northern Blvd) and the City Map street center lines around
tax lots **1 + 70**. Queue item B-07 (Lane B; plan ID M2-05, multi-lot site math). Tax lot 70's
own records (215-16 Northern Blvd, the competitor-review benchmark) are in
`../benchmark_215_16_northern/` (queue item B-01) and are not copied here.

Why these two lots: DOB BIS job 421803891 (in the B-01 pack, `dob_bis_jobs_ic3t-wcy2_bin_4157401.json`)
is an alteration filed "TO REFLECT ONE (1) ZONING LOT AND (2) TAX LOTS (LOT #1 & #70)". That is
evidence of a filing. It does **not** verify a zoning lot, and nothing in this pack does: the
multi-lot result keeps the zoning-lot status at "Check needed".

- **Capture:** 4 official responses on 2026-10-01 between 22:17:33 and 22:17:40 UTC. Python `urllib`
  GET, keyless, one request per file, sequential, at least 2.5 s apart, all HTTP 200 on the
  first attempt. Each body is stored byte-for-byte as returned.
- **Provenance:** `MANIFEST.json` lists, for each file, the dataset, source id, connector URL
  builder, exact URL, `retrieved_at` (UTC), HTTP `Date` and `Last-Modified`, status, byte count
  and sha256. `dcm_envelope_epsg2263` is the street query envelope.
- **Integrity:** `services/api/tests/spatial/test_multi_lot_site_benchmark_block_7334.py`
  re-hashes every file and rebuilds every URL with the connectors' own builders.
  `.gitattributes` (`-text`) keeps the bytes exact.

| File | Source | What it holds |
|---|---|---|
| `mappluto_lot_4073340001_epsg2263.json` | MapPLUTO (DCP_GIS `MAPPLUTO`), `Version` 26v2 | Lot 1 outline in EPSG:2263 feet (4 corners; `Shape__Area` 9,922.45) |
| `pluto_64uk-42ks_bbl_4073340001.json` | PLUTO `64uk-42ks`, row `version` 26v2 | `lotarea` 9925, `lotfront` 99.25, `lotdepth` 100, `zonedist1` R6B, `overlay1` C2-2 |
| `dcm_street_centerline_envelope_lots_1_70.json` | DCM street center line, layer last edited 2025-12-01T19:39:55Z | The 6 segments within 150 ft of lots 1 + 70: Northern Boulevard "100" (53832), 215 Place "60" (11453), 215 Street "60" (3134, 3656, 16384), 45 Road "50" (2821) |
| `dcm_layer_metadata.json` | DCM layer metadata | `editingInfo.dataLastEditDate` (street-width dataset version, B-04) |

## Readings on the recorded data (tests in `test_multi_lot_site_benchmark_block_7334.py`)

Planar EPSG:2263 measurements, 0.01 ft. They are tax-map approximations, not a survey.

| Selection | Lot type | Frontage | Outline area | City records area |
|---|---|---|---|---|
| Lot 70 | corner | 215 Place 99.98 ft; Northern Boulevard 103.88 ft | 10,387.99 sq ft | 10,075 (+3.11 %) |
| Lot 1 | corner | 215 Street 99.98 ft; Northern Boulevard 99.25 ft | 9,922.45 sq ft | 9,925 (−0.03 %) |
| Lots 1 + 70 | corner | 215 Street 99.98 ft; Northern Boulevard 203.13 ft; 215 Place 99.98 ft | 20,310.44 sq ft | 9,925 + 10,075 = 20,000 (+1.55 %) |

Lots 1 and 70 share one lot line of 99.98 ft (their vertices coincide exactly). It is removed from
the combined outline. Street widths (B-04): Northern Boulevard wide (100 ft mapped), 215 Place and
215 Street narrow (60 ft mapped).

Existing buildings stay per lot (B-05 on the B-01 DOB records): both lots read "Unknown — enter".
Lot 1 sets aside 14,150 and 39,772 sq ft (DOB jobs 421199072 and 421803891). Lot 70 sets aside
39,934 sq ft (DOB NB 440608941). These figures are never added together.

Gap in lot 1's evidence: the B-01 pack was captured for lot 70. Lot 1's B-05 result reads the
pack's DOB BIS job filings (`ic3t-wcy2`) for two buildings: BIN 4157401, whose rows sit on lot 1
(jobs 421199072 and 421803891 among them), and BIN 4616079, whose job 421240534 names lot 1 in
its lot column and lot 70 in its BBL column. Certificate-of-occupancy lookups for BIN 4157401
were recorded in both datasets (DOB BIS `bs8b-p36w` and DOB NOW `pkdm-hqz6`) and returned no
rows. No query keyed on BBL 4073340001 was recorded: no DOB NOW job filings (`w9ak-ipjd`) and
no certificates of occupancy by BBL. Lot 1 reads "Unknown — enter" either way.
