# M1-T001 Producer Report — Official-source research: PLUTO / MapPLUTO (continuation run)

- **Task ID:** M1-T001
- **Producer agent:** official-source-researcher
- **Date:** 2026-07-16
- **Requested status:** `awaiting_gate`
- **Run history:** Run 1 (2026-07-16, worktree `agent-ab7d30546f58c0a85`) was network-denied and returned `blocked` with a fetch plan (§5 of the prior version of this report). The orchestrator executed that plan and committed `project-control/reports/M1-T001-fetch-evidence.md` (E1–E7). Run 2 (this run, worktree `agent-a7f911e9c1dcee512`, task worktree designation `main-tree-research-only`) produced the deliverables from that stored evidence only — no network calls were attempted in this run, per ADR-005 and the 2026-07-15 evidence-capture directive.

## 1. Files created (complete list; only allowed paths touched)

1. `docs/research/pluto-mappluto-2026-07-16.md` — full findings for S1–S5 with per-claim evidence citations (E1–E7 + official URL + retrieval date 2026-07-16), [NEEDS G1 RE-VERIFICATION] markers on every search-summary/summarizer-paraphrase claim, 11-item OPEN QUESTIONS table, contract-test fixture pack, connector plan.
2. `docs/research/source-registry-drafts/pluto-mappluto.json` — array of two source-registry records (`nyc-dcp-pluto-soda`, `nyc-dcp-mappluto-bulk`), each with all PRD §8.2 fields plus an `open_questions` array; JSON null for unknowns; no invented values.
3. `project-control/reports/M1-T001-producer-report.md` — this file (overwrites the run-1 blocked report; run-1 denial content summarized above and preserved in git history at commit f11b970's successor history).

## 2. Commands run (this run)

- No network commands (prohibited for this run; evidence is pre-captured).
- JSON validation of the registry draft:

```
python -c "import json;d=json.load(open(r'...\docs\research\source-registry-drafts\pluto-mappluto.json',encoding='utf-8'));print('valid JSON; records:',len(d));..."
```

Output (actual):

```
valid JSON; records: 2
keys r1: ['agency', 'api_dataset_identifier', 'authentication', 'connector_implementation', 'fallback_source', 'fields_available', 'geographic_coverage', 'health_status', 'known_limitations', 'last_successful_ingestion', 'latest_source_version', 'name', 'official_url', 'open_questions', 'rate_limits', 'source_id', 'source_type', 'terms_usage_notes', 'update_frequency']
keys r2: [same 19 keys]
```

## 3. Acceptance scenarios S1–S5 → evidence mapping

| Scenario | Status | Where satisfied | Evidence basis |
|---|---|---|---|
| S1 — distribution channels, dataset IDs, formats | DONE (with flagged gaps) | research doc §2 | E1 (`api/views/64uk-42ks.json`), E2 (live SODA `resource/64uk-42ks.json?$limit=1`), E3 (`api/views/f888-ni5f.json`), E4 (README PDF direct read), E5/E6 (search-verified — marked [NEEDS G1 RE-VERIFICATION]) |
| S2 — PLUTO vs MapPLUTO, version scheme, archive | DONE (archive URL open) | research doc §3 | E4 verbatim release model (quarterly major / monthly minor, 24v1 / 24v1.1 naming), E3/E4 product distinction, E6 archive statement flagged for G1 (OQ-4) |
| S3 — data dictionary, fields, units, nulls | PARTIAL-BY-DESIGN, gaps explicit | research doc §4 | Dictionary located (E5, title-verified); 73 SODA fields verbatim (E2); NumFloors null convention + condo billing-BBL semantics verbatim (E4); all per-field units/null conventions listed as OQ-5, not guessed |
| S4 — channel discrepancies, priority order | DONE | research doc §5 | Stale 22v3 attachments and frozen 2013 timestamps on f888-ni5f (E3) vs current 26v1 README (E4); live version-current SODA (E2); priority argued per PRD §8 with Socrata token rules (E7) |
| S5 — source-registry draft, all PRD §8.2 fields | DONE | registry JSON | Two records, 19 keys each (validated above), open_questions arrays, nulls for unknowns |

## 4. Key verified facts (for the gate's convenience; full citations in the research doc)

- PLUTO tabular = Open Data `64uk-42ks`, live SODA endpoint, serving `version = "26v1"` on 2026-07-16 (E2).
- MapPLUTO Open Data `f888-ni5f` is href-type (no SODA resource), quarterly, with stale 22v3 attachments and 2013-frozen timestamps (E3).
- Official README 26v1 (direct PDF read, E4): quarterly major / monthly minor release model; minor releases touch zoning attributes only; condo one-record-per-complex billing-BBL semantics; Marble Hill/Rikers idiosyncrasies; DATES OF DATA input-vintage table; new 26v1 fields MIHOption1-4 / TrnstZone / AffResFAR / ManuFAR; NumFloors null convention; DCP disclaimer; PLUTOChangeFile ships with MapPLUTO.
- Socrata app tokens optional; tokenless = shared IP-pool throttling; tokened = unthrottled unless abusive; 429 on throttle; `X-App-Token` header preferred (E7).

## 5. Recommended channel priority (per PRD §8, argued from evidence)

- **PLUTO facts:** SODA `64uk-42ks` with `X-App-Token` when available (tier 2 — no tier-1 dedicated API exists), DCP bulk CSV fallback for full imports and version pinning (tier 3).
- **MapPLUTO geometry:** DCP bulk FileGDB shoreline-clipped primary (tier 3; only verified full-fidelity channel); Open Data `f888-ni5f` treated as a catalog pointer only; ArcGIS feature service unverified pending OQ-3.
- **Stale-attachment channel lag** on the portal is recorded as a concrete S4 discrepancy; freshness monitoring must poll the SODA `version` field, not Socrata metadata timestamps.

## 6. What remains open for G1 (11 open questions; full table in research doc §8)

OQ-1 raw Socrata timestamps for `64uk-42ks` (summarizer reported future-dated values); OQ-2 full SODA column list via the `api/views` columns array (single-record sample omits null fields: zonedist2-4, overlay1-2, spdist1-3, ltdheight, landmark, histdist, appbbl, condono...); OQ-3 ArcGIS feature-service endpoint (JS-rendered page); OQ-4 exact bulk download sizes/URLs and archive URLs (nyc.gov 403 to evidence session); OQ-5 field-level units and null conventions from the data dictionary (fields enumerated in the doc; flagged for G1 or a follow-up capture); OQ-6 minor-release propagation lag on SODA; OQ-7 data-dictionary direct-fetch confirmation; OQ-8 NYC Open Data terms of use; OQ-9 f888-ni5f href target; OQ-10 clipped/unclipped file names + geometry CRS; OQ-11 PLUTOChangeFile location/format.

## 7. Assumptions and defaults

- Assumed the orchestrator-captured evidence file faithfully records the 2026-07-16 fetches (ADR-005 division of labor). Direct quotes were treated as evidence; summarizer paraphrases and search-result summaries were treated as pointers and marked [NEEDS G1 RE-VERIFICATION] in the deliverables.
- Assumed the task's `main-tree-research-only` worktree designation means deliverables belong at the repository-root paths named in the task contract.
- No units, CRS, code meanings, endpoints, or URLs were assumed beyond what the evidence states; every such gap is an explicit open question.

## 8. Known limitations

- Worked from stored evidence only (`project-control/reports/M1-T001-fetch-evidence.md`); no independent live verification in this run. G1 (data-contract-verifier) should re-verify the [NEEDS G1 RE-VERIFICATION] items, especially E5/E6-based claims.
- S3 is deliberately partial: the authoritative data dictionary is located but not field-extracted; the registry records therefore mark units/null conventions as pending rather than asserting them.
- nyc.gov page-level facts (download links/sizes/archive) remain unverified due to bot protection (HTTP 403) in the evidence session.

## 9. Security / provenance impact

- None negative. No code, schema, or connector touched. Deliverables strengthen provenance: per-record `version` capture and input-vintage (DATES OF DATA) tracking are specified for the future connector.

## 10. Recommended next tasks

1. **PLUTO SODA connector task** (M1/M2): implement `pluto-soda` per the plan in research doc §7 with the fixture pack in §6; requires a Socrata app token (human action: create at the Socrata/NYC Open Data developer settings — record exact steps at G1).
2. **Data-dictionary field-extraction capture**: fetch `pluto_datadictionary.pdf` (E5 URL) and extract units/null conventions/code lists for the OQ-5 field list; closes most of S3's open surface. Small, orchestrator- or browser-capable session.
3. **MapPLUTO bulk-import task** (M2): Render-worker FileGDB→PostGIS import per research doc §7, after OQ-4/OQ-10 close.
4. **Remaining M1 source-family research packets** (PRD §8.1): Zoning Tax Lot Database, GIS Zoning Features, Zoning Resolution, DOB NOW, ACRIS, landmarks, flood — reuse the fetch-plan → orchestrator-capture → stored-evidence pattern proven here.

## 11. Report path

`project-control/reports/M1-T001-producer-report.md`
