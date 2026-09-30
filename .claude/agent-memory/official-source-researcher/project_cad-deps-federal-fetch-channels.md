---
name: cad-deps-federal-fetch-channels
description: Which official channels fetch reliably for DXF/CAD spec, npm deps provenance, npm advisories, and federal public-domain drawing corpora (D-087 research family)
metadata:
  type: project
---

Reliable vs blocked official channels for the D-087 CAD-export / 3D / phase-C-PDF-reader research
family (observed 2026-09-24, task M5-T084). Complements [[nyc-source-fetch-channels]].

**DXF / Autodesk (official spec):**
- `https://images.autodesk.com/adsk/files/acad_dxf.pdf` curls fine (HTTP 200, application/pdf,
  1.75 MB) — it is the **AutoCAD 2005 DXF Reference** (© Autodesk, version u19.1.01). Authoritative
  and byte-stable for the *structural* group codes (LINE/LWPOLYLINE/POLYLINE-VERTEX-SEQEND/3DFACE/
  TEXT/LAYER/LTYPE, value-type ranges, handles). PyMuPDF (`fitz`) is installed locally and extracts
  its text cleanly (use `PYTHONIOENCODING=utf-8` — some glyphs break cp1252 stdout).
- Version-SENSITIVE facts must come from the CURRENT page: `help.autodesk.com/cloudhelp/<year>/ENU/
  AutoCAD-DXF/files/GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A.htm` (HEADER Section Group Codes) —
  WebFetch works; swap `<year>` (2016/2017/2026) to BRACKET when a code appeared.
- `autodesk.com/support/technical/article/...drawing-version-codes-for-autocad.html` **403s** to
  curl+browser-UA — use the DXF HEADER page instead (documented fallback).
- Load-bearing DXF facts found: **$INSUNITS 21 = US Survey Feet** (22/23/24 = survey inch/yard/mile),
  introduced in the **AutoCAD 2017** DXF reference (2016 stops at 20=Parsecs) — matters for EPSG:2263.
  Handles "always enabled as of AutoCAD Release 13" ([A2005] p.184) ⇒ **R12/AC1009 is the
  handles-optional, no-OBJECTS/CLASSES writer target** for a hand-written DXF writer.

**npm dependency provenance + advisories:**
- `registry.npmjs.org/<pkg>` full JSON has the `time` map (per-version publish UTC) needed for the
  604800 s age gate, plus per-version `license`/`dependencies`/`peerDependencies`/`scripts`/
  `dist.integrity`. Scoped names URL-encode the slash: `@react-three%2Ffiber`. `three` uses a 0.x
  scheme — pick "newest ≥7d-old" by **publish time**, not naive semver-max (an ancient 1.58.1 outsorts
  0.186.0).
- Advisories without local npm: `api.osv.dev/v1/querybatch` (POST; empty `{}` per query = no vuln;
  aggregates GHSA) cross-checked with `api.github.com/advisories?ecosystem=npm&affects=<pkg>[@ver]`
  (the `affects=pkg@ver` form filters by version — returns 0 when the pkg's advisories predate the
  pinned version). ALWAYS run a positive control (e.g. `lodash@4.17.11` → 7 GHSAs) so an empty result
  is proven genuine, not an outage. Top-level only — whole-tree audit stays the G5 admission packet's job.

**Federal public-domain drawing corpora (phase-C PDF reader fixtures):**
- Library of Congress `loc.gov/item/<id>/?fo=json` and `loc.gov/search/?q=...&fo=json&c=N` return
  `resources[].files[][]` with `mimetype`/`size`/`url` and an item `rights_advisory`. curls fine with a
  browser UA. HABS/HAER/HALS measured-drawing **sheets are raster TIFF, not PDF** (masters on
  `tile.loc.gov/storage-services/master/...`); the only PDFs are the **data pages** (scanned + OCR,
  `/Producer` = "Paper Capture Plug-in"). Rights: "No known restrictions on images made by the U.S.
  Government" ⇒ PD (17 USC §105).
- VA CFM Technical Information Library: legacy DIRECT detail PDFs still resolve
  (`cfm.va.gov/til/sDetail/sDetail-Div23-PDF-1.pdf` / `-2.pdf` = HVAC, born-digital VECTOR CAD-plotted,
  `/Producer` "Acrobat PDFMaker … for AutoCAD") but the TIL **index** now 302→JS portal
  `vatilms.va.gov/vatilms/reports/PG-18-4` (no static links to a non-browser fetch) — only Div-23
  survived at the legacy path; other divisions need a browser capture. Federal work ⇒ PD (NCS
  title-block standard is a copyrighted 3rd-party doc — record as a caveat, don't block fixtures).
- Classify vector vs scanned by inspecting bytes with PyMuPDF: many `page.get_drawings()` paths + 0
  image XObjects ⇒ vector; one image XObject/page + OCR text ⇒ scanned. Downloads go to
  `%TEMP%\d087-corpus\` only, never the repo (thin client; <50 MB).

**Why:** M5-T084 (D-087 research) hit all of these exactly; the autodesk-support 403 and the VA-portal
JS migration each cost a fetch round, and the three-0.x semver trap silently picked a 2013 version.

**How to apply:** for any future CAD-export / 3D-dep / drawing-corpus research packet, route DXF facts
to the acad_dxf.pdf + cloudhelp DXF HEADER pages, deps to registry.npmjs.org + OSV/GitHub-advisories
(positive-controlled), and PD drawing fixtures to LoC `?fo=json` (scanned) + VA legacy sDetail (vector).
