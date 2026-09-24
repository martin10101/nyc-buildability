# bridge_ring_pairs — provenance (M5-T073, DB-045(a), D-084-R002)

Real parcel ring PAIRS for the offline bridge-mount precondition harness
(`services/api/tests/connectors/test_bridge_ring_preconditions.py`). Each pair
binds the SAME BBL's two accepted representations:

- **display ring** — EPSG:4326, display-only, `mappluto_lot_outline`
  (`f=geojson&outSR=4326`);
- **authoritative ring** — EPSG:2263 US survey feet, `mappluto_geometry_arcgis`
  (`f=json`, wkid 102718 / latestWkid 2263).

> **[ORCH-CORRECTED per M5-T073 data-contract review F1, 2026-09-24]: this file's two
> sections below describe the PRE-HARVEST state and apply to P01–P04 ONLY.** The harvest
> WAS executed on 2026-09-23 (commit 06e3e72d): pairs **P05–P08** are net-new
> orchestrator-captured pairs whose raw bodies are stored DIRECTLY in this directory
> (`P05…/P08…/{display_4326.json, authoritative_2263.json}`), captured through the two
> accepted connectors' own query builders over the official NYC DCP MapPLUTO ArcGIS
> endpoint per the recipe in `HARVEST_SPEC.md` (keyless GET, `Accept: application/json`,
> raw body bytes written verbatim, sha256 over the exact UTF-8 body bytes, recorded as
> `kind: raw_esri_body` / `raw_geojson_body` in the manifest). Dataset-release split,
> body-verified per side: **P01–P04 pair a 26v2 display ring against a 26v1 authoritative
> ring** (cross-release, captures ~54 days apart); **P05–P08 are 26v2/26v2** (same-second
> captures). The live sample is **8 pairs / 5 boroughs / 7 geometry classes**; the
> per-pair area figures in the manifest `notes` are PLUTO **LotArea** values (not the
> geometry's `Shape__Area`). The authoritative account of every pair is
> `pairs_manifest.json` (per-side `dataset_version`, digests, expected verdicts) plus the
> producer report's `[ORCH-HARVEST]` section; the original text below is preserved
> verbatim per the report-preservation convention.

## Byte source (single source of truth, no fabrication, no drift)

The verbatim response bodies are **already stored** as VERBATIM live-captured
official bytes in two accepted fixture packs, and are referenced here by path +
recorded sha256 rather than duplicated:

- display 4326 — `services/api/tests/fixtures/mappluto_lot_outline/` (task
  M5-T020, D-040-R001; LOT01/LOT03/LOT05/LOT06 are `classification: raw`);
- authoritative 2263 — `services/api/tests/fixtures/mappluto_geometry/` (task
  M2-T009; MPG02/MPG04/MPG06/MPG07 are `classification: raw`).

The binding registry is [`pairs_manifest.json`](pairs_manifest.json). The harness
reads both bodies OFFLINE and re-hashes the authoritative `response_body_raw`
against the recorded `response_body_sha256` (identical byte basis — compact
single-line JSON, no embedded newlines — so the digest round-trips exactly). The
display body's sha256 is computed and echoed; the source pack records the display
digest over the stored file bytes (a different basis), so it is carried as
`source_file_sha256` for provenance, not asserted.

## Bound of this real sample (honest, D-051 discipline)

The overlap of the two accepted packs gives **4 real single-lot pairs across 2
boroughs** (Manhattan ×3, Queens ×1) and 4 geometry classes:

| pair_id | BBL | borough | geometry class |
|---|---|---|---|
| P01_regular_block_1008350041 | 1008350041 | Manhattan (1) | regular single-exterior block lot (Empire State Bldg) |
| P02_many_vertex_waterfront_1000010010 | 1000010010 | Manhattan (1) | many-vertex irregular holed waterfront (Governors Island) |
| P03_large_assemblage_condo_billing_1000157501 | 1000157501 | Manhattan (1) | large assemblage / condo billing merged complex |
| P04_multipolygon_waterfront_4142600001 | 4142600001 | Queens (4) | true MultiPolygon, shoreline-clipped |

The packet's **≥8 pairs / ≥3 boroughs / a genuinely small regular lot** are NOT
reachable from the accepted packs alone and require new live captures through the
two connectors. Live capture needs network egress this offline worker does not
have, so that remainder is **routed to harvest** — never fabricated — with an
exact, re-runnable procedure in [`HARVEST_SPEC.md`](HARVEST_SPEC.md). The harness
discovers harvested pairs through `pairs_manifest.json` with no code change.
