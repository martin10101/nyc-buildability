---
name: survey-document-source-channels
description: Live-verified access facts for NYC survey/tax-map/recorded-doc/plan sources (DTM ArcGIS, ACRIS, DOB plans, DWG) — reusable for document-ingestion source research
metadata:
  type: project
---

Survey / official-document source channels, live-verified 2026-08-05 (M2-T014 Packet A). Companion to
[[nyc-source-fetch-channels]].

- **DOF Digital Tax Map (DTM) = the machine tax-map/tax-lot channel.** ArcGIS FeatureServer
  `services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer`
  (anonymous, no token; layer 0 TAX_LOT_POLYGON, layer 1 TAX_BLOCK_POLYGON; tables 2-19 incl
  MAPLIBRARY_MAP/CONDO/AIR_LOT/SUB_LOT/REUC_LOT/DAB_*/PTS_*). **CRS = EPSG:3857 (wkid 102100/3857)** —
  DIFFERENT from the DCP chain's EPSG:2263; reproject before overlay. `maxRecordCount 1000` -> paging.
  Rate signal is a response header `x-esri-org-request-units-per-min: usage=..;max=28800` (not a JSON
  quota). `Last-Modified` header is a real freshness signal. Open Data twin: TAX_LOT_POLYGON `i38t-6if2`
  (Socrata, dict XLSX `e044ecb0-...`). Legacy blob `smk3-tmxj` is RETIRING by Oct 2025 — do not build on it.
- **ACRIS = two-tier.** INDEX metadata is on Socrata (Real Property Legals `8h5j-fqxa` gives
  borough/block/lot + `document_id` = the BBL->document join, ~22.7M rows; Master `bnx9-e6tj` has
  document_id/crfn/reel_*; **no image URL in any column**). Document IMAGES are viewer-only at
  `a836-acris.nyc.gov` and the register **actively blocks automation**: `GET /DS/DocumentSearch/Index`
  307-redirects to `/BandwidthPolicy/ACRIS-BW-POL.html`, whose text references "detection of automated
  scripts/robots that are capturing data" and routes bulk to a **paid subscription** (City Register
  212-487-6300). => ACRIS images = NO authorized programmatic access; manual upload only; NEVER bypass.
- **DOB plans/drawings have no API.** DOB NOW Public Portal (`a810-dobnow.nyc.gov`) is a human viewer with
  *some* newer digital plan uploads viewable; most approved plans are borough-office microfilm or require a
  formal records request behind an **eFiling login**. DOB Open Data = filing METADATA only, not drawings.
  => manual upload for the plan; metadata proves the filing exists.
- **Licensed boundary/topographic survey (class 1, highest weight) exists in NO public NYC system** — it's
  private (owner/surveyor/title/lender). DTM/MapPLUTO polygons are administrative (class 2), never a
  substitute. This is why a document-ingestion pipeline here is an UPLOAD pipeline, not a scraper.
- **DWG format = DEFER, never promise.** Proprietary Autodesk, no official public spec (Library of Congress
  FDD `fdd000445`); full read/write libs are licensed (Autodesk RealDWG "selective/non-competitive"; ODA
  library = commercial membership, spec reverse-engineered R13->2018). Safe path: require export to
  **vector PDF** (turns CAD into the supported PDF path) or DXF via a future validated converter. DXF has a
  public Autodesk spec + open readers (ezdxf) but sandbox/testability unproven -> convert/defer initially.

**Why:** M2-T014 needed honest available/restricted/unavailable findings; the ACRIS bandwidth-policy
redirect and the licensed-survey no-public-system fact are the load-bearing negative cases.

**How to apply:** For any future NYC recorded-document / plan / tax-map source research, reuse these
channels; treat ACRIS images + DOB plans + licensed surveys as manual-upload (do not design bypasses);
always check DTM's EPSG:3857 vs 2263 mismatch; steer CAD to vector PDF.
