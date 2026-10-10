# Evidence pack: 215-16 Northern Boulevard

Research date: October 10, 2026. Start with **215-16-Northern-research-handoff.md**.

## Quick document navigation

- **Current tax map:** official-pdfs/taxmap_40733420210729120533_0.pdf, page 1.
- **2017 split:** official-pdfs/taxmap_40733420170322143246_0.pdf, page 1; data/dtm_block7334_9.json, transaction 76338.
- **Earlier map:** official-pdfs/taxmap_40733420140108123603_0.pdf, page 1.
- **Proposed zoning floor-area scope:** official-pdfs/pw1_userguide.pdf, page 14, sections 12B/12C.
- **Short-block exception:** official-pdfs/law_23_344.pdf, page 2; side-line exception, page 4.
- **Dwelling units:** official-pdfs/law_23_52.pdf, pages 2–3.
- **Street-history lead:** official-pdfs/citymap_cp4366.pdf, one sheet. This does not establish a parcel-specific widening.
- **ACRIS:** data/acris_legals_keydocs.json and data/acris_master_all.json are index entries only.
- **Geometry:** site-boundary-diagram.png and geometry-calculations.json. All calculated dimensions are GIS, not survey measurements.

## Reproducibility

`source-manifest.json` gives source requests, retrieval timestamps and SHA-256 hashes. Official files are included unchanged. `page-images` contains rendered pages or labeled source crops; these are convenience views. The code and diagram are original analysis, separately identified.

To reproduce the geometry and PNG, run `python build_geometry.py` with Python 3 and matplotlib installed. It reads `data/mappluto.json` and writes a `derived` folder. All block parcel geometries are retained in that response so adjacency can be checked; unrelated ownership/assessment fields were omitted in the official query.

The ACRIS good-through date is September 30, 2026. No ACRIS instrument images, deed Schedule A, survey or approved ZD1 are included. See `access-log.json` and the handoff for the exact missing documents and access limitations.
