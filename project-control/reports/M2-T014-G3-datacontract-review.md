# G3 GATE REPORT — M2-T014 (Survey & official-document source/format research, Packet A)

> Verbatim return from the independent data-contract-verifier (transport entity-decoding only).
> Recorded by the orchestrator. The separately-rostered security-reviewer agent could not run
> (Fable 5 usage limit); its security dimension is substantively covered within this review
> (SR-S7 no-bypass check below), and its independent confirmation is deferred to Fable 5 availability
> (non-blocking).

**Verdict: PASS**

**Reviewer:** independent (data-contract-verifier + security-reviewer discipline), read-only
**Reviewed SHA:** ed12721 on `task/M2-T014-survey-research`, worktree `C:/Users/MLFLL/Downloads/nyc-zoning/t14`
**Review date:** 2026-08-05 UTC
**Method:** Read all deliverables at the frozen SHA; independently spot-verified every material live claim against the current official endpoints/pages (not from the producer's fixtures). Producer conclusions treated as claims to reproduce.

## Independent spot-verification results (SR-S7)

Every check below was run by the reviewer against the live official source, independent of the producer's stored fixtures:

| # | Claim | Live result | Verdict |
|---|---|---|---|
| 1 | DTM ArcGIS FeatureServer `DTM_ETL_DAILY_view` — layers 0/1 + tables 2–19, maxRecordCount 1000, wkid 102100/3857 | Fetched `?f=pjson` live: layers 0 `TAX_LOT_POLYGON`, 1 `TAX_BLOCK_POLYGON`; tables 2–19 names all match exactly; maxRecordCount 1000; wkid 102100 / latestWkid 3857 | EXACT MATCH |
| 2 | Per-BBL query returns `{BBL 1000010010, BORO 1, BLOCK 1, LOT 10, LOT_NOTE null, EFFECTIVE_TAX_YEAR 2026-2027}`, anonymous, EPSG:3857 | Fetched live: identical attributes, spatialReference 3857, no token needed | EXACT MATCH |
| 3 | ACRIS viewer `DS/DocumentSearch/Index` → HTTP 307 → `BandwidthPolicy/ACRIS-BW-POL.html` | Reproduced with curl: `HTTP/1.1 307 … Location: https://a836-acris.nyc.gov/BandwidthPolicy/ACRIS-BW-POL.html` | EXACT MATCH |
| 4 | DTM Open Data `i38t-6if2` = DOF TAX_LOT_POLYGON, created 2024-10-16, documented column set | Fetched `api/views`: DOF provenance, created 2024-10-16, 858,055 rows, column names match | MATCH (see column-count note) |
| 5 | Legacy blob `smk3-tmxj` "retired by October 2025" | Fetched `api/views`: verbatim "This downloadable file will be retired by October 2025" | EXACT MATCH |
| 6 | ACRIS Legals `8h5j-fqxa` — 14 columns, ~22.7M rows, no image-URL column (BBL→document_id join) | Fetched live: 14 columns identical, 22,688,577 rows, no image URL | EXACT MATCH |
| 7 | ACRIS Master `bnx9-e6tj` — documented 14 columns, no image-URL column | Fetched live: 14 columns identical, no image URL | EXACT MATCH |
| 8 | DWG proprietary, no published spec; ODA spec reverse-engineered (R13→2018); RealDWG selectively licensed | Corroborated via LC FDD fdd000445 + ODA/RealDWG sources | CORROBORATED |
| 9 | CRS hazard: DTM EPSG:3857 vs DCP/MapPLUTO chain EPSG:2263 | DTM 3857 verified live; EPSG:2263 grounded in accepted registry §2/§4; ±20 ft caveat grounded | GENUINE HAZARD, correctly flagged |
| 10 | No access-restriction/bypass path proposed | ACRIS images, DOB plans, tax-map sheet PDFs all recorded manual/restricted; explicit "do NOT enumerate/guess/scrape/bypass"; STOP on login+payment | CONFIRMED — no violation |

No fabricated verification: only checks reproducible live are marked MATCH; DWG is documentary corroboration (LC FDD returned 403 to WebFetch, verified via LC-indexed search + independent ODA/RealDWG sources).

## Per-scenario findings

- **SR-S1 inventory completeness — PASS.** Every named family investigated with an explicit finding; retrieval dates 2026-08-05 on all citations.
- **SR-S2 seven-way class matrix — PASS.** All seven classes with evidentiary weight, can/cannot-establish, and five explicit non-interchangeability rules; no conflation.
- **SR-S3 format policy — PASS.** All seven formats have explicit verdicts; DWG = DEFER with licensing/sandboxing/testability analysis; DXF = CONVERT/DEFER; no format promised without a proven path.
- **SR-S4 authorized-access proof — PASS.** Live-fetched stable URLs/dataset IDs for every AVAILABLE source; "manual upload required" for every source without one. No guessed endpoints.
- **SR-S5 negative case — PASS.** Three honest negatives (ACRIS images, DOB plans, licensed surveys).
- **SR-S6 registry rows — PASS.** Seven draft rows + seven additive canonical rows (§11.1–§11.7) with owner-mandated fields.

## Required corrections

**Blocking:** none.

**Non-blocking (recommend fixing on any future touch; do not hold the gate):**
1. Column-count label: `survey-document-sources-2026-07.md` §1.2(b) and `SOURCE_ACCESS_REGISTRY.md` §11.2 state `i38t-6if2` has "17 columns," but 16 are listed and the live `api/views` returns 16. Correct to 16 or name the 17th field.
2. FeatureServer org provenance: add a one-line note tying the Esri org `services6.arcgis.com/yG5s3afENB5iO9fj/...` to the Open Data "Digital Tax Map Feature Server" cross-link (producer tracks as OQ-A2).
3. Byte-level additivity of §11: asserted and structurally consistent; orchestrator can confirm with `git diff` at merge if desired.

## Security review

No login/CAPTCHA/viewer-control/bandwidth-policy bypass is designed or documented. The single tax-map-sheet PDF probe was a direct fetch of a keyless public URL (HTTP 200), not stored, with an explicit prohibition on programmatic enumeration. Payment (ACRIS subscription) and credentialed (DOB eFiling) paths are recorded as STOP conditions, not automated. Forbidden paths respected. No violation.

**Overall verdict: PASS** — SR-S1..SR-S6 satisfied; independent SR-S7 spot-verification confirms every material live claim with exact fidelity; no access-restriction violation; only cosmetic non-blocking corrections. (Recording of the gate result is the orchestrator's action; the reviewer is read-only and did not run project_control, git, or gh.)
