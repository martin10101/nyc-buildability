# M2-T013 — V1/V2 Positional-Accuracy Verification

**Task:** M2-T013 spatial-intersection engine — in-task source verification of the
per-input positional-accuracy records (advisory §4 items V1/V2).
**Verified by:** orchestrator (lead session) · **Retrieval date:** 2026-07-21 (UTC)
**Method:** official NYC DCP / DOF metadata, retrieved and text-extracted (pypdf) or
read via web search. Small extracts only; no bulk documents retained in the repo.

## Outcome summary (drives `services/api/app/spatial/policy.py` accuracy registry)

| Input | value_ft | basis | evidence |
|---|---|---|---|
| nyzd (base zoning) | 20.0 | **documented** | `nyzd_metadata.pdf` "The estimated horizontal accuracy is +/- 20 feet" (advisory G1-confirmed, research `zoning-features-ztldb-2026-07-16.md:149`) |
| nyco / nysp / nysp_sd / nylh / nyzma | 20.0 | **assumed** | per-layer figure NOT individually verifiable in-task (V2 below); fail-safe 2×-band sensitivity active |
| MapPLUTO lot polygon | 20.0 | **assumed** | official MapPLUTO metadata publishes NO positional-accuracy figure (V1 below) |

The engine stamps `basis` on every intersection result and escalates to
professional review whenever an `assumed`-basis classification would flip if the
true accuracy were 2× the assumed value (advisory §2.6.7). Keeping the five
non-nyzd layers and the MapPLUTO lot at `assumed` is the conservative,
fail-closed direction — an evidence-backed upgrade to `documented` would REDUCE
review triggers, so it is deliberately not done without per-source confirmation.

## V1 — MapPLUTO / DTM horizontal accuracy → NOT DOCUMENTED

- Source: NYC DCP MapPLUTO metadata, `meta_mappluto.pdf`
  (https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/meta_mappluto.pdf),
  retrieved 2026-07-21, text-extracted with pypdf (96,816 chars).
- Finding: the document contains **no horizontal/positional-accuracy figure**. The
  only accuracy-related text is warranty language ("DCP does not warranty the
  completeness, accuracy, content, or fitness…") and per-field descriptions
  (frontage/depth "measured in feet"). Corroborated by web search across the
  MapPLUTO/PLUTO metadata and data-dictionary set (no `+/- feet` positional figure).
- Lineage: MapPLUTO geometry derives from the DOF **Digital Tax Map (DTM)** Tax Lot
  Polygon feature class (PLUTO README / DCP resource page). DOF publishes the DTM
  through the Digital Tax Map / Property Information Portal; no `+/- feet`
  horizontal-accuracy figure was located in-task.
- Decision: MapPLUTO lot accuracy stays **`basis: assumed`** at 20.0 ft (analogy to
  the documented nyzd figure via shared cadastral lineage). Permanent and visible
  until DOF/DCP publishes an official DTM/MapPLUTO positional-accuracy figure.

## V2 — Per-layer accuracy for nyco/nysp/nysp_sd/nylh/nyzma → NOT INDIVIDUALLY DOCUMENTED

- nyzd (base zoning): **documented +/- 20 feet** — `nyzd_metadata.pdf`
  (https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nyzd_metadata.pdf),
  already G1-confirmed (advisory §1). Unchanged.
- Dataset-level corroboration: the DCP "NYC GIS Zoning Features" resource states the
  dataset's "estimated horizontal accuracy is +/- 20 feet" and that the features were
  developed from DCP Tax Block Base Map files, DOITT NYCMap planimetrics, and zoning
  maps (web search, 2026-07-21). This is a DATASET-level statement, not a per-layer
  metadata figure.
- Per-layer check: `nysp_metadata.pdf`
  (https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nysp_metadata.pdf),
  retrieved 2026-07-21, text-extracted with pypdf (34,272 chars): the extract contains
  **no** `Positional_Accuracy` / "estimated" / "+/- 20 feet" statement. The
  `www.nyc.gov` metadata mirrors returned HTTP 403 to the fetch client, so nyco /
  nysp_sd / nylh / nyzma per-layer PDFs were not directly text-verified in-task.
- Decision: nyco / nysp / nysp_sd / nylh / nyzma stay **`basis: assumed`** at 20.0 ft,
  matching the advisory's open OQ-5. The dataset-level +/- 20 ft is recorded as
  supporting (not per-layer-confirmed) evidence; upgrading these layers to
  `documented` is deferred to a future direct read of each layer's own metadata,
  because the safe direction is to keep the fail-safe active, not to relax it.

## Reproducibility / hygiene

- Metadata PDFs were fetched to the session tool-results area (outside the repo) and
  text-extracted; no bulk documents were committed. Only this small dated extract
  enters `docs/research/`. Local disk footprint negligible.
