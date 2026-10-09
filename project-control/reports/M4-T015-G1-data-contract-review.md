# G1 GATE REPORT — M4-T015 (DCM Street Center Line street-width connector)

> Orchestrator note: reviewer return saved VERBATIM from the agent-return channel
> (transport entity-decoding only). Reviewer: data-contract-verifier. Recorded by the
> orchestrator per ADR-005.

All checks complete. Only 3 Python files reference the new modules (the connector + its two test files); the classifier is imported only by the connector. No consumer wiring in rules/api/profile/scenario/spatial — scope is clean.

Here is my full G1 report.

---

**Gate:** G1 — official-source data-contract verification
**Reviewer:** data-contract-verifier (independent; not the producer)
**Task:** M4-T015 — D-045 B2 connector build (ArcGIS primary, fail-closed-to-narrow width classification)
**Material commit:** 8538c272 (per packet); primary-checkout HEAD b3e66078 (unchanged)
**Anchor:** `git rev-parse --show-toplevel` = `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (primary checkout); HEAD = `b3e66078…`. I ran NO git state-changing command.

## What I ran (and did not run)

Ran (read-only):
- MANIFEST self-consistency: recomputed sha256 + byte-count of all 26 fixtures vs `MANIFEST.json` on disk → **ALL_CONSISTENT**, no orphans/missing, 26 fixtures.
- **Live byte-verification** (WebFetch against the keyless endpoint, network reachable):
  - Layer metadata `.../FeatureServer/0?f=json` — name, geometryType, maxRecordCount, objectIdField, wkid/latestWkid, `dataLastEditDate`, full 18-field name list.
  - West 100 St two-segment query (live).
  - OBJECTID=20420 (Sharrott Ave) and OBJECTID=599 (Jay Place) live.
- `python -m pytest tests/connectors/test_dcm_street_centerline_arcgis.py tests/connectors/test_dcm_street_width_classifier.py -q` → **131 passed**.
- `python -m pytest tests/connectors -q` → **619 passed** (no regression).
- `python tools/modularity_check.py --check` → **EXIT 0** (failures 0; 17 warnings) and `--report`.
- Read: packet, producer report, evidence-map, M4-T013 research, registry draft, both connector modules, both test files, 3 fixture files, MANIFEST.
- Grep for consumers of the new modules.

Did NOT run: any `project_control.py`/git/gh/write command (read-only reviewer). Did not need orchestrator-captured evidence — my sandbox had live network + Python.

## Per-mandate findings

**1. Live byte-verification / fabrication check — PASS.**
Three fixtures verified against the live source with exact attribute matches, including subtle values:
- `west_100_st_two_segments.json`: live OBJECTID 7719 = `Streetwidth "60"`, 14471 = `"100"`, both `Mapped_St`/`City_St`/`Record_ST=N`/`Paper_ST=N` — matches fixture and research E6 exactly.
- `unmapped_street_override_wide.json` (OBJECTID 20420): live = `Not_mapped`/`Feat_status=Way_on_record`/`Streetwidth "80"`/`Record_ST=N`/`Paper_ST=N`/`Build_Status=Improved`, with `HonoraryNM/Old_ST_NM="None"` (literal string) — byte-identical to the stored fixture.
- `paper_street_override_wide.json` (OBJECTID 599): live = `Mapped_St`/`Streetwidth "80"`/`Record_ST=N`/`Paper_ST=Y` — matches.
- Metadata `dataLastEditDate=1764617995374` (2025-12-01T19:39:55Z) matches the fixture and the research pin. No drift observed since capture. This evidences genuine live captures, not fabrication. The one synthetic fixture (`provider_error_http200_synthetic.json`, 114 bytes) is a legitimate documented ArcGIS 400 error shape, `synthetic:true`, `url:null`, per the M2-T009 precedent.

**2. Field semantics / units / CRS — PASS.**
Live layer field names are exactly `OBJECTID, Borough, Feat_Type, Feat_status, Street_NM, HonoraryNM, Old_ST_NM, Streetwidth, Route_Type, RoadwayType, Build_Status, Record_ST, Paper_ST, Stair_ST, CCO_ST, Marg_Wharf, Edit_Date` (+ `Shape__Length`). The connector's `OUT_FIELDS` matches these 17 attribute names verbatim — the full live ArcGIS names, NOT the truncated shapefile/SODA names (`streetwidt/feat_statu/roadway_typ/build_stat`). Field-name honesty verified live; nothing guessed. CRS: `outSR=2263` on every query; `wkid 102718/latestWkid 2263` validated (`WrongCRSError`) before any field is trusted; geometry returned by default but ignored (OQ-4 out of scope) so no CRS mixing occurs in any measurement. Raw `Streetwidth` preserved VERBATIM (`streetwidth_raw` and `width_classification.raw_text`, including `None`).

**3. Classifier fail-closed contract — PASS.**
Verified the code against the research fail-closed rule and the E7 domain: wide ONLY on clean numeral/decimal ≥75, range with BOTH endpoints ≥75, or strict/non-strict `>`/`>=` inequality with bound ≥75. Every ambiguous class (straddling ranges incl. `60-75`, `74-75.3`; `<`/`>`-inequalities on the ambiguous side; `<=75`/`>=` edge handling; approximations/prose incl. `Probably between 80-90`; `Width Irregular`; `varies`; `n/a`; `Unknown`; `Unknown but <75`; `Unknown but >75`; `Regular but unknown.`; empty/None; non-string; negative; catch-all) → `narrow_fail_closed` + typed class + `review_required=True`. The strict/non-strict distinction at exactly 75 is correct (`<75` confident-narrow, `<=75` ambiguous). Mapped-street override (`_mapped_street_override`) keys ONLY on `Feat_Type`/`Paper_ST`/`Record_ST`, never on `Feat_status`; a wide raw read is suppressed to narrow for paper/record/unmapped/former/unrecognized-Feat_Type, and can never make a narrow read more permissive. The producer report's class→disposition table matches `AMBIGUITY_CLASS_DISPOSITIONS` and the code branches exactly; `test_every_documented_class_is_exercised_by_this_suite` locks table↔suite together. OQ-1/OQ-3 surfaced, never resolved.

**4. Producer disclosures a–c:**
- **(a) three live-source refinements — PASS, honestly recorded and correctly handled.** `Record_ST/Paper_ST` live `Y`/`N` domain: verified live (599 `Paper_ST=Y`; West 100 St `N`) and the override keys on `=="Y"`, not `"yes"`. `Build_Status` coded-value domain `DCMSCL_route_status_1={Improved,Part_improved,Unimproved,Not_applicable(code 'n/a')}`: present in the live metadata I fetched and in the fixture bytes — correctly recorded in draft + report, treated as typed passthrough only. `Feat_status='Way_on_record'` with `Record_ST='N'` on OBJECTID 20420: verified live — the independence claim is genuine and the override provably does not key on `Feat_status`.
- **(b) no mappluto import — ACCEPTABLE.** The connector imports only from its sibling classifier + stdlib; no other connector is imported or edited (forbidden_paths intact). The producer's reasoning (mappluto exports are BBL/polygon-specific with no analog in the street-segment domain; `raw_body_digest` is a 2-line local helper) is sound. The connector-discipline precedent favors focused modules over cross-connector coupling; the M5-T020 bounded no-retry posture is reused structurally. Disclosed, not silent.
- **(c) empty_or_missing unit-test-only — ACCEPTABLE.** Live `Streetwidth IS NULL`/`=''` returned 0 rows; proven by `classify_street_width(None)`/`("")` unit tests; never fabricated as a fixture. Honors the never-fabricate rule.

**5. Upstream error + paging + provenance — PASS.**
HTTP-200 ArcGIS `error` object → typed `UpstreamError` (never data), verified by test and by the synthetic fixture (code 400). `exceededTransferLimit`/`resultOffset` paging honored with loop-safety guards (duplicate-page, repeated-OBJECTID overlap, zero-progress, hard page ceiling) — each a typed `PagingPathologyError`; single-attempt no-retry transport (M5-T020 posture). Predicates are bounded/allowlisted (Borough domain, safe-text+SQL-escaped Street_NM, positive-int OBJECTID, bounded `IN(...)`≤50) — no citywide sweep, no caller SQL. Provenance on `StreetSegmentQueryResult`: `source_id`, `service_root`, `layer`, `retrieved_at`, `source_data_last_edited(_ms)` freshness pin, `metadata_request_url`, `raw_digests`, `drift_signals`, `attribution`, `disclaimer`, `page_urls`, `correlation_id`. SODA fallback carries the ~16-month staleness caveat in the registry; the connector correctly does not query SODA.

**6. Registry draft posture — PASS.**
M2-T009 shape preserved (source_id, agency, endpoint, auth, rate_limits, update_frequency, geographic_coverage, fields_available, terms, connector_implementation, known_limitations, fallback_source, open_questions). `draft_status` non-final. `self_declared_source_id` = `"nyc-dcp-dcm-street-centerline-arcgis"` matches the connector `SOURCE_ID` constant exactly. Three refinements tagged `M4-T015`, with both the PDF wording and the live discrepancy recorded (no silent "correction").

## Corrections

- **ADVISORY (route to G4 / qa-engineer; blocking for acceptance per gate-verdict semantics):** The producer report §9 states "neither new module … appears in the warning list." This is **factually incorrect**: `tools/modularity_check.py --check` lists `services/api/app/connectors/dcm_street_centerline_arcgis.py` (959 lines) as `review_signal: above the justification threshold; record a cohesion justification in review`. CI is EXIT 0 (non-blocking), and on the merits the module is cohesive (single connector surface; classifier correctly split out). But policy (CLAUDE.md item 16; `.claude/rules/code-architecture.md` item 6) requires a recorded cohesion justification for a file above the justify threshold, and the report both omits it and denies the flag. The producer should correct §9 and record the cohesion justification. This is outside the G1 data-contract mandate; I surface it for the G4 reviewer.
- **ADVISORY (minor):** Segment queries do not set `returnGeometry=false`, so production requests pull polyline geometry that this task ignores (OQ-4). Thin-client-tolerable at the bounded query sizes here; consider disabling until geometry is consumed.
- **OBSERVATION (not a defect):** Provenance is at the query-result envelope level, not per-segment. Full per-fact provenance mapping (source_id/timestamp/BBL/confidence/conflict) belongs to the later consumer-wiring task, which is explicitly out of scope here.

## Conclusion

Every G1 data-contract mandate item (1–6) passes: the connector's contract with the official DCM ArcGIS source is correct and live-verified, field semantics/units/CRS are honest and evidenced, the fail-closed classifier is mathematically sound and matches the pinned M4-T013 research, fixtures are genuine live captures (byte-verified against the live source; the one synthetic is correctly marked), upstream-error/paging/provenance are complete, and disclosures (a)–(c) are honestly recorded and correctly handled. The single material correction (modularity report inaccuracy + missing cohesion justification) is an advisory G4 item that does not undermine the data contract but should be resolved before acceptance.

**VERDICT: PASS**
