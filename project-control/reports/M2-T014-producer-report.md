# M2-T014 Producer Report — Survey & official-document source/format research (Packet A)

- **Task:** M2-T014 (research-only; owner directive 2026-07-20 Packet A; dispatch hold lifted by owner 2026-08-04)
- **Producer agent:** official-source-researcher
- **Worktree / branch:** `C:/Users/MLFLL/Downloads/nyc-zoning/t14` on `task/M2-T014-survey-research` (base frozen main `d5d9b50`)
- **Retrieval anchor:** all live retrievals **2026-08-05 UTC** (server-clock from response `Date`/`Last-Modified` headers; local session date 2026-08-04)
- **Requested status:** `awaiting_gate` (G0/G2/G3; reviewers data-contract-verifier + security-reviewer)

## 1. What was investigated (every official system family named + discovered) — SR-S1

| System | Method | Finding |
|---|---|---|
| DOF Digital Tax Map — ArcGIS FeatureServer | live `?f=pjson` + per-BBL `/query` (HTTP 200) | **AVAILABLE** (anonymous; EPSG:3857; maxRecordCount 1000) |
| DOF DTM — NYC Open Data `i38t-6if2` | live `api/views` (HTTP 200) | **AVAILABLE** (Socrata; dict XLSX attached) |
| DOF DTM legacy blob `smk3-tmxj` | live `api/views` | **RETIRING by Oct 2025** (do not use) |
| DOF tax-map SHEET PDFs (Property Information Portal) | live probe (HTTP 200 application/pdf) | **RESTRICTED** (generation-stamped URL, no stable API) |
| DOB filing metadata (DOB NOW/BIS Open Data) | prior accepted research (registry §6/§7) | **AVAILABLE (metadata only)** |
| DOB plans / site plans / drawings | official guidance (portal manual + records guide) | **RESTRICTED → manual upload required** |
| ACRIS document IMAGES (`a836-acris.nyc.gov`) | live viewer probe (HTTP 307 → BandwidthPolicy) + policy read | **NO AUTHORIZED PROGRAMMATIC ACCESS** |
| ACRIS index metadata (`bnx9-e6tj`, `8h5j-fqxa`) | live `api/views` (HTTP 200) | **AVAILABLE (metadata only; BBL→document_id)** |
| DCP MapPLUTO / Zoning Features / footprints | registry §2/§4 + note | **AVAILABLE (not survey evidence)** |
| Licensed boundary/topographic survey | reasoned negative (no public system) | **NO PUBLIC SYSTEM → manual upload required** |

Every citation is retrieval-date-stamped (2026-08-05). Fixtures with reproducible curl commands:
`docs/research/fixtures/m2-t014/`.

## 2. SR-S1..SR-S7 coverage

- **SR-S1 (inventory completeness):** COVERED — every named family (DOB NOW/BIS filings+attachments, DOF DTM, DCP datasets, ACRIS images) + discovered systems (ACRIS index, DTM sheet PDFs, Property Information Portal, licensed-survey negative) each has an explicit available/restricted/unavailable finding with retrieval dates. `survey-document-sources-2026-07.md` §0–§8.
- **SR-S2 (seven-way class matrix):** COVERED — `survey-document-sources-2026-07.md` §9: each of the 7 classes defined with evidentiary weight, can/cannot-establish, and 5 explicit non-interchangeability rules.
- **SR-S3 (format policy):** COVERED — `docs/SURVEY_DOCUMENT_FORMAT_POLICY.md`: all 7 formats have explicit verdicts; DWG = DEFER with licensing/sandboxing/testability analysis (LC FDD + ODA + RealDWG cited); DXF = CONVERT/DEFER-initial; no format promised without a proven path.
- **SR-S4 (authorized-access proof):** COVERED — `survey-document-sources-2026-07.md` §10: each AVAILABLE source cites a live-fetched stable URL/API (no guessed endpoints); each without one is recorded "manual upload required".
- **SR-S5 (negative case):** COVERED — THREE honest negatives: ACRIS document images (automation explicitly prohibited), DOB plans (no API), and licensed surveys (no public system). Primary = ACRIS images with verbatim bandwidth-policy evidence.
- **SR-S6 (registry rows):** COVERED — `docs/research/source-registry-drafts/survey-document-sources.json` (7 rows) + additive canonical rows `docs/SOURCE_ACCESS_REGISTRY.md` §11.1–§11.7.
- **SR-S7 (G3 walkthrough):** READY for the independent reviewer — all live claims have fixtures + exact URLs to spot-verify; no access-restriction violation is proposed (ACRIS/DOB/portal all recorded as manual/restricted, never bypassed).

## 3. STOP conditions hit (recorded, not acted on)
- ACRIS "subscription data services" = **payment** → STOP (not procured; owner-only).
- DOB records request via **eFiling login** = credentialed → STOP (not automated).
- No terms-of-use ambiguity encountered (ACRIS automation prohibition is explicit). No accounts created; no external emails sent.

## 4. Files written (all inside allowed_paths)
- `docs/research/survey-document-sources-2026-07.md` (inventory + 7-class matrix)
- `docs/SURVEY_DOCUMENT_FORMAT_POLICY.md` (format decision matrix)
- `docs/research/source-registry-drafts/survey-document-sources.json` (7 draft rows)
- `docs/SOURCE_ACCESS_REGISTRY.md` (ADDITIVE §11 only — no existing row modified)
- `docs/research/fixtures/m2-t014/` — `dtm_taxlot_query_1000010010.json`, `dtm_taxlot_query_headers.txt`, `dtm_taxlot_layer0_meta.json`, `acris_viewer_307_headers.txt`, `README.md`
- `project-control/reports/M2-T014-producer-report.md` (this file)

Forbidden paths respected: no `services/**`/`apps/**`/`packages/**`; no bypass code/doc; no bulk downloads (largest stored fixture 17 KB; the 2 MB tax-map PDF probe was NOT saved); no `project-control/**` beyond this report; no `.claude/**`.

## 5. Self-check / limitations
- CRS hazard flagged: DTM is EPSG:3857 vs DCP EPSG:2263 — must reprojection-validate before overlay.
- XLSX data-dictionary content (DTM `e044ecb0-...`) not extracted (octet-stream; cloud deferral, OQ-A1).
- DOB NOW Public Portal digital-plan coverage depth not quantifiable without the browser viewer (OQ-A3).
- Building-footprints dataset noted but not deep-verified (OQ-A4) — out of the survey core.
- The 2 MB tax-map sheet PDF reachability was confirmed (HTTP 200) but the file was deliberately not stored (thin-client budget) and its URL is generation-stamped (not a stable identifier).

## 6. Requested status
`awaiting_gate` — ready for independent G3 review (data-contract-verifier spot-verifies live claims against official pages; security-reviewer confirms no access-restriction/bypass is proposed). Producer cannot self-accept.
