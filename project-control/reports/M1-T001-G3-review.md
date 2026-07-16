# M1-T001 — G3 Independent Walkthrough Gate Review

- **Task:** M1-T001 — Official-source research: PLUTO / MapPLUTO
- **Gate:** G3 (independent human-style walkthrough)
- **Reviewer:** code-reviewer (independent; did not produce the work, did not run G1)
- **Review date:** 2026-07-16
- **Verdict:** **PASS** (3 minor editorial/coherence defects, none blocking; reproducible evidence below)
- **Method:** Started from the acceptance criteria in `project-control/tasks/M1-T001.json` (S1–S5), consumed the post-correction deliverables as a downstream connector implementer would, verified every G1 correction C1–C6 in the files at HEAD (corrections commit `e178adb`, confirmed in git history), and re-ran all four G1 SODA spot-tests **live** against the official endpoint (network was available to this session). Read-only except this report file. No project_control.py, no git writes.

Artifacts reviewed (in this order — producer report last, per G3 discipline):
1. `project-control/tasks/M1-T001.json` (S1–S5 checklist)
2. `docs/research/pluto-mappluto-2026-07-16.md` (post-C1–C6)
3. `docs/research/source-registry-drafts/pluto-mappluto.json` (post-C1–C6)
4. `project-control/reports/M1-T001-G1-verification.md` (G1 PASS + C1–C6)
5. `project-control/reports/M1-T001-fetch-evidence.md` (E1–E7)
6. `project-control/reports/M1-T001-producer-report.md` (read last)

---

## 1. Walkthrough table

| # | Check | Expected | Actual | Evidence |
|---|---|---|---|---|
| W1 | C1 applied: MIH SODA fieldNames in registry record 1 | `mih_opt1`–`mih_opt4`, not `mihoption1-4` | `"mih_opt1", "mih_opt2", "mih_opt3", "mih_opt4"` present in `dictionary_known_fields_not_in_sample` | `pluto-mappluto.json` line 46 |
| W2 | C2 applied: verified Socrata timestamps in doc §2.1 and §5.1(4) | rowsUpdatedAt 2026-05-28T19:50:48Z; summarizer misconversion noted; registry freshness caveat softened to secondary-signal | All present; §2.1 marked [RESOLVED AT G1 — see G1 report §1.1]; §5.1(4) marked RESOLVED — C2; registry `known_limitations` says "usable as a secondary freshness signal; version-field polling remains primary" | doc lines 30, 187; json line 60 |
| W3 | C3 applied: db-pluto archived, active repo data-engineering | §2.4 and §9/E6 corrected | §2.4: "archived since 2023-07-13; the active official build repository is `NYCPlanning/data-engineering`. Do not cite db-pluto as authoritative"; §9 E6 row matches | doc lines 54, 264 |
| W4 | C4 applied: ArcGIS FeatureServer as verified secondary channel | Endpoint + DCP_GIS + 26v1 + EPSG:2263 + maxRecordCount 2000 in §2.5, §5.2, registry record 2 | All three locations updated; role explicitly "verified secondary/per-lot query channel", bulk FileGDB remains citywide-import primary | doc lines 56–63, 197; json lines 98, 101 |
| W5 | C5 applied: 108-column inventory | §4.2 + registry record 1 note the 108 columns, `geom`, 8 per-input date columns, firm07/pfirm15/dcpedited/notes/ownertype/appdate; §4.6 CRS wording | §4.2 [RESOLVED AT G1 — full column inventory; C5] block present verbatim; §4.6 states dictionary-verbatim State Plane + EPSG:2263 from the ArcGIS side; registry `fields_available.note` matches | doc lines 150, 172; json line 23 |
| W6 | C6 applied: BBL serialization hazard + qt5r-nqxp fixtures | F12–F14 in §6; registry `known_limitations` + fallback companion channel | F12 (BBL `"1000010100.00000000"` normalization), F13 (400 `query.soql.no-such-column`), F14 (`qt5r-nqxp`) all present; registry lines 61–62, 64 carry both findings | doc lines 221–223; json lines 61–64 |
| W7 | Spot-test normal | `$select=version&$limit=1` → `[{"version":"26v1"}]` | **Live 2026-07-16: exact match** `[{"version":"26v1"}]` | curl, this session |
| W8 | Spot-test boundary | `$select=bbl&$order=bbl&$limit=2&$offset=1` → number-typed BBL with trailing decimals | **Live: `[{"bbl":"1000010100.00000000"},{"bbl":"1000010101.00000000"}]`** — stable ordering; serialization hazard reproduced exactly as F12 warns | curl, this session |
| W9 | Spot-test missing | `?bbl=9999999999` → `[]` | **Live: `[]`** | curl, this session |
| W10 | Spot-test failure | `$select=nonexistent_col` → HTTP 400, `errorCode: query.soql.no-such-column` | **Live: HTTP 400**, body `"errorCode":"query.soql.no-such-column"` — F13 signature exact | curl, this session |
| W11 | Registry PRD §8.2 completeness | All 18 §8.2 fields per record | Both records carry all 18 fields + `open_questions`; 19 keys validated (matches producer's JSON check); nulls used where unknown (`last_successful_ingestion: null`, `rate_limits: null` for bulk); `health_status: "unverified"` honest | json both records |
| W12 | Priority-order consistency (S4) | Same order in doc §5.2, registry fallbacks, producer plan | Consistent everywhere: PLUTO = SODA `64uk-42ks` primary + DCP bulk CSV fallback; MapPLUTO = DCP bulk FileGDB clipped primary, ArcGIS FeatureServer verified secondary/per-lot, `f888-ni5f` pointer-only | doc §5.2; json `fallback_source` fields |
| W13 | Downstream usability | PLUTO connector implementable without re-research | Yes: endpoint, auth/token model, 429/400 failure signatures, null-omission caveat, condo billing-BBL semantics, units/null conventions, version/provenance capture, 14-fixture pack, drift check — all specified. Only bulk-import mechanics (OQ-4/OQ-10 residuals) remain, needed for the M2 MapPLUTO bulk task, correctly deferred and not guessed | doc §4–§7 |
| W14 | Open items exactly as claimed | Only OQ-4 residual, OQ-10 residual, OQ-6 window open | Confirmed. §8 ledger matches the G1 §3 ledger row-for-row. OQ-5/OQ-11 "residuals" are deferred extraction from already-verified sources (dictionary appendices, qt5r-nqxp columns) at connector build — deferred work, not unknowns. Notably, fetch-evidence E6 contained search-summary gdb names (`Mappluto.gdb`/`Mapplutounclipped.gdb`) that were correctly **not** promoted into the deliverables — no guessing around the 403 | doc §8; fetch-evidence E6 |
| W15 | Hygiene: no citywide data / large artifacts / credentials | KB-scale text only; no secrets | Deliverables 32,716 B + 12,013 B text; credential-pattern grep over docs/research = no matches; low-storage statements intact (Render worker import, bounded temp, Supabase `gis-imports` upload, temp cleanup; F11 HEAD-only). Only >2MB files outside `.git` live in `_quarantine/` (38 MB, gitignored line 63, untracked) — pre-existing M0-T005-era quarantine, unrelated to M1-T001 | `ls -la`, `find -size +2M`, `git check-ignore`, grep |

Scenario coverage mapping: S1 → W7/W11/W12 + doc §2 (all channels evidenced, none guessed); S2 → doc §3 (verbatim release model, 26v1 live-confirmed at W7); S3 → W5 + doc §4 (dictionary-verified units/nulls; gaps are explicit OQs); S4 → W12 + doc §5.1 (stale 22v3 attachments, frozen 2013 timestamps, tabular channel current); S5 → W11.

## 2. Defects (all minor, none blocking)

1. **D1 (minor, coherence):** `docs/research/pluto-mappluto-2026-07-16.md` line 42 (§2.2) still reads "The URL the href entry points to was not captured — **[NEEDS G1 RE-VERIFICATION]** (OQ-9)" while §8 marks OQ-9 **RESOLVED** and §5.2(3) states the verified href target. Stale marker; a reader following the OQ-9 pointer does reach the correct resolution, so factual harm is nil.
2. **D2 (minor, coherence):** doc line 193 (§5.2 PLUTO item 2) retains "(E6, [NEEDS G1 RE-VERIFICATION])" on the archive statement. Post-G1 status is "partially resolved, OQ-4 residual" (§3.5); the marker should say that instead.
3. **D3 (minor, coherence):** `pluto-mappluto.json` record 2 `authentication.notes` (line 80) still says "download mechanics need G1 re-verification (OQ-4)" although G1 has completed; should read "OQ-4 residual — needs a browser-capable session against nyc.gov".

No guessed schemas, no hard-coded legal values (FAR fields correctly labeled informational, "not a substitute for the rules engine"; BldgArea explicitly flagged as NOT ZR §12-10 floor area), no hidden defaults, no silent uncertainty (every unknown is a ledgered OQ), no provenance or low-storage violations.

## 3. Correction confirmation

All six G1 corrections **C1–C6 verified applied** in the working tree at commit `e178adb` (W1–W6 above, exact line locations cited).

## 4. Recommendation to the orchestrator

**PASS.** Accept M1-T001. Optionally fold the three stale-marker fixes (D1–D3) into acceptance as an editorial fixup, or carry them as notes into the PLUTO connector task packet. Carry-forwards for the connector/import tasks: (a) BBL number-type normalization to 10-digit strings (F12 — reproduced live in this review); (b) 400/`query.soql.no-such-column` as the schema-drift signature (F13); (c) OQ-4/OQ-10 residuals must close via a browser-capable session before the M2 MapPLUTO bulk import; (d) OQ-6 minor-release propagation observation across the next 26v1.x boundary; (e) Socrata app token is a human action at connector build.

## 5. Reproduction commands (run live 2026-07-16 by this reviewer)

```
curl -s 'https://data.cityofnewyork.us/resource/64uk-42ks.json?$select=version&$limit=1'
  → [{"version":"26v1"}]
curl -s 'https://data.cityofnewyork.us/resource/64uk-42ks.json?$select=bbl&$order=bbl&$limit=2&$offset=1'
  → [{"bbl":"1000010100.00000000"},{"bbl":"1000010101.00000000"}]
curl -s 'https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=9999999999'
  → []
curl -s -w '%{http_code}' 'https://data.cityofnewyork.us/resource/64uk-42ks.json?$select=nonexistent_col'
  → 400, {"errorCode":"query.soql.no-such-column",...}
git show --stat e178adb   # corrections commit
git check-ignore -v _quarantine/   # .gitignore:63; untracked (38 MB, pre-existing, unrelated)
```
