# Derivation fixtures (M5-T051, D-076 phase B1)

Hand-computed fixture pack for `app.scenario.derivation.derive_proposal`. Every expected
value below is computed BY HAND (arithmetic shown), never by running the module — no
self-proving fixtures. All coordinates are EPSG:2263 (US survey feet); all integer-valued
coordinates and their products stay well under 2^53, so the shoelace sums and axis-aligned
distances are exact in float64 (the tests assert exact equality).

Common conventions:
- **Footprint area** = shoelace on the base outline (unsigned; order/winding-independent).
- **Lot coverage** = footprint / the CALLER-SUPPLIED `lot.area_sq_ft` (a separate provided
  datum with its own provenance — never computed from the lot-line geometry).
- **Per-level plate area** = the level's own outline where present, else the base outline.
- **Gross floor area** = sum over levels of `plate_area x floor_count` (no deductions).
- **Level height** = `floor_to_floor_ft x floor_count`; **cumulative** = their sum.
- **Wall setback** = minimum distance from the wall segment to the supplied lot-line
  segments; **street setback** = distance to the attested street line for that `wall_id`,
  or a typed honest absence when none is supplied.

## rectangle_100x80.json

Base outline: axis-aligned rectangle, x in [1000000, 1000100] (100 ft), y in
[200000, 200080] (80 ft).

- Footprint = 100 x 80 = **8000 sf**.
- Lot area (supplied) = 16000 sf → coverage = 8000 / 16000 = **0.5**.
- Per-level areas: both levels use the base outline → level 0 = **8000 sf**,
  level 1 = **8000 sf** (`base_outline`).
- Gross = 8000 x 1 (level 0, floor_count 1) + 8000 x 2 (level 1, floor_count 2)
  = 8000 + 16000 = **24000 sf**.
- Heights: level 0 = 12.0 x 1 = **12.0 ft**; level 1 = 10.0 x 2 = **20.0 ft**;
  cumulative = 12 + 20 = **32.0 ft**.
- Lot lines: a uniform 15 ft frame — south y=199985, north y=200095, west x=999985,
  east x=1000115. Each wall's nearest lot line (parallel side AND both corners) is exactly
  15 ft away, so **every wall lot-line setback = 15.0 ft**.
- Street: an attested line on the SOUTH frontage at y=199960. South wall (y=200000) →
  200000 - 199960 = **40.0 ft** (`derived`, carries the attestation identifiers). The
  east/north/west walls have no attested street line → **typed honest absence**
  (`absent_no_attestation`).

## l_shape_multilevel.json

Base outline: an L — the 100 x 80 rectangle with a 40 x 40 notch removed from the
top-right corner. Vertices (local, +[1000000,200000]): (0,0)(100,0)(100,40)(60,40)
(60,80)(0,80).

- Footprint via shoelace = 8000 (full rect) − 1600 (40 x 40 notch) = **6400 sf**
  (shoelace 2A = 12800 → A = 6400).
- Lot area (supplied) = 12800 sf → coverage = 6400 / 12800 = **0.5**.
- Per-level: level 0 uses the base L → **6400 sf** (`base_outline`); level 1 has its own
  40 x 40 outline → 40 x 40 = **1600 sf** (`own_outline`).
- Gross = 6400 x 1 + 1600 x 3 = 6400 + 4800 = **11200 sf**.
- Heights: level 0 = 12.0 x 1 = **12.0**; level 1 = 11.0 x 3 = **33.0**; cumulative =
  **45.0 ft**.
- South lot line at y=199990; south wall (y=200000) → 200000 - 199990 = **10.0 ft**. No
  street lines supplied → the south wall's street setback is a typed honest absence.

## wall_setback.json

Base outline: 50 ft (x) x 30 ft (y) rectangle, x in [1000000, 1000050], y in
[200000, 200030]. Two named walls: `front` (bottom edge, y=200000) and `rear` (top edge,
y=200030).

- Footprint = 50 x 30 = **1500 sf**; lot area 3000 → coverage **0.5**; single level height
  10.0 x 1 = **10.0 ft**; gross = 1500 x 1 = **1500 sf**.
- ONE lot line supplied: `front_lot_line` at y=199982.
  - `front` wall (y=200000) → 200000 - 199982 = **18.0 ft**.
  - `rear` wall (y=200030) → 200030 - 199982 = **48.0 ft**.
- Street line for `front` at y=199975 → 200000 - 199975 = **25.0 ft** (`derived`, carries
  the attestation `source_raw_digest`/`classification_basis`/…).
- `rear` has NO attested street line → **typed honest absence**
  (`absent_no_attestation`), never a default distance.
