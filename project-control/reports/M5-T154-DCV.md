# M5-T154 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `7adc476edb171f16386981708c06c0c7dddf995d` (branch `task/wave22-site-context`, review copy `read in place (/root/project/w-wave20)`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R843, R936, R937.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. The reviewers' required corrections (code M5-T154-C1; QA C1,C2; security advisory A1) were all applied before the frozen head and I confirmed the fixes here: test_flag_off_returns_none_and_makes_no_connector_call now asserts zero connector calls with counting spies; test_manifest_lists_exactly_the_recorded_files + test_file_bytes_match_manifest_sha256 (all 3 recordings) + test_pack_has_readme_and_byte_exact_gitattributes are present and green; _resolve_inside path containment is present with test_recorded_pack_loader_refuses_a_path_escaping_the_pack. All passed in my run.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-11 00:41 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

````
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T154 (directive D-090, 3 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only; I produced none of this work or its records. This is not a human or professional review. I treated every report, gate record, evidence map, printed page and the brief as an unverified claim and re-derived each result from primary evidence (the code, the tests and what they assert, the recorded pack, the printed pages, the git objects, the registry). The only writes I avoided entirely; I ran the directive validator once and the three authorized focused tests only.

(1) HEAD VERIFIED
 - `git -C /root/project/w-wave20 rev-parse HEAD` = 7adc476edb171f16386981708c06c0c7dddf995d on branch task/wave22-site-context, working tree clean; all file reads and checks below are at this frozen head.
 - Merge-base of the head with the stated base main 9ab3a47e6a55fc75e13140e910f0839541754874 is exactly 9ab3a47e6a55 (that base is an ancestor); claim-seam head f68c60267c983c756f314c2b03628279a1bfc63a is present in the branch log.
 - The frozen head (the submit commit) differs from the gate-recording head 2341590e only in project-control/ files; every product file is byte-identical across 6c8c9f7d (CI/corrected head) -> 2341590e (gates) -> 7adc476 (frozen), so there is one product content identity.

(2) ROWS
ROW D-090-R843 — PASS
 - This task's share is the DATA a site plan needs for adjoining context; I built the 1.1.0 map document from the recorded pack via app.api.v1.report_context.recorded_pack_provider and saw contract_version "1.1.0" with tax_lots (status available, 200 neighbour entries, subject 4073340070 absent), building_footprints (available), streets (available) and context_window {xmin 1048388.63, ymin 215910.44, xmax 1049311.58, ymax 216831.10} = subject bbox +/-400 ft.
 - Each layer carries source and date in provenance (tax_lots source_id nyc-dcp-mappluto-arcgis, source_data_last_edited 2026-09-09; streets nyc-dcp-dcm-street-centerline-arcgis, 2025-12-01; footprints nyc-oti-building-footprints-arcgis, 2026-09-27) and the measurement basis is EPSG:2263 US survey feet (map_context crs/units/measurement); a refused layer becomes layer_unavailable with its reason and the provider never raises (test_a_refusing_fetcher_makes_only_that_layer_unavailable passed), so a drawing can state the limitation.
 - The printed pages (print-w22g page 3) show the data drawn: lot outline, neighbouring lots, existing building footprints, street names with mapped widths (NORTHERN BOULEVARD 100 ft / 215 STREET, 215 PLACE, 216 STREET 60 ft), edge-length dimensions (103.88/99.98/99.98/101.71 ft), a north arrow, a real scale bar, a legend, and a captioned source/date/"nothing is surveyed" measurement basis.
 - Stays open for the rest: the drawn-plan content is M5-T155 (drawings) and M5-T156 (report), whose verification rows for R843 are still pending (verifier ""); yards/setbacks are deliberately not drawn (ruling Y6, engine work not done) and are shown as "Not known"/"Not worked out yet" — that engine work remains owed and the row stays open in the registry for the sibling tasks.

ROW D-090-R936 — PASS
 - This task's share is fetching and recording the surroundings; I independently re-derived with shapely that lot 4073340001 shares 99.9765 ft with the subject (within 0.01 ft of the 99.98 ft line), lot 4073340011 shares 101.709 ft and lot 4073340061 shares 2.2244 ft, and that streets are named with mapped widths Northern Boulevard 100, 215 Place 60, 215 Street 60 — matching S7.
 - The connector requests no personal field: OUT_FIELDS = (OBJECTID, BBL, Block, Lot, Address, Version) in app/connectors/mappluto_window_arcgis.py:109, and the recorded MapPLUTO window (201 features) has attribute keys exactly {Address, BBL, Block, Lot, OBJECTID, Version} with zero OwnerName hits.
 - The printed site plan (page 3) and block close-up (page 2) render the lot among its surroundings: streets drawn as streets with names and mapped widths, the Northern Boulevard x 215 Place corner, neighbouring lots and existing buildings, with the sheet named ("What constrains the design?" / "Where is the lot?") — not an isolated outline.
 - Stays open for the rest: naming and rendering the site drawing for the reader is M5-T155/M5-T156 work; their R936 verification rows are still pending (verifier "").

ROW D-090-R937 — PASS
 - This task's share is the two windows and their provenance; I confirmed the streets window = subject bbox +/-1,000 ft {xmin 1047788.63, ymin 215310.44, xmax 1049911.58, ymax 217431.10} and the lots/footprints context_window = +/-400 ft, each layer carrying source_id and source_data_last_edited.
 - The printed location sheet (page 2) renders a neighbourhood map with the subject lot marked and a 0-1,000 ft scale bar, and a block close-up with a 0-400 ft scale bar, each captioned with its source and last-edited date in plain words (DCM "edited 1 Dec 2025", MapPLUTO "edited 9 Sep 2026", footprints "edited 27 Sep 2026") and no URL, field name or code word — the context maps of DB-222.
 - The requirement is satisfied at neighbourhood scale ("city or neighbourhood scale"); a separate city-overview map is not produced (ruling Y10 uses neighbourhood + block), which is within the row's "or".
 - Stays open for the rest: the location-page rendering is M5-T156 work and M5-T155's drawings; their R937 verification rows are still pending (verifier "").

(3) BINDING B1–B5
 - B1: PASS. The requirements.json diff base..head appends M5-T154 (alongside M5-T155/M5-T156) to R843's applicability.task_ids and adds R936/R937 as new rows already carrying M5-T154; the only removed lines in the whole diff are requirement_count 933->940, updated_at, and two trailing task_ids re-commas — no requirement's "text" field was modified. Rows R934-R940 are new this wave and their text equals the source-082/083 reading tables (quoted fragment + orchestrator reading) with matching source_ref and classification; the validator (below) confirms no post-capture source/digest tampering.
 - B2: PASS. tools/directive_registry.sha256_text_artifact(requirements.json) = 99bcd267cee2fb1bf8414f79d12daf0d961f3fc8c4053511abc6cb9bbb5da235 equals manifest.requirements_content_digest_sha256 (identical). `python tools/validate_directive_compliance.py --check` exited 0 (direct exit code).
 - B3: PASS. verification.json has exactly one M5-T154 row, applicable_requirement_ids = [D-090-R843, D-090-R936, D-090-R937], producer geospatial-engineer, verifier "" (empty), reviewed_sha null, and each of the three requirements state "pending" with empty evidence.
 - B4: PASS. reg.evaluate_task_refs(M5-T154 packet) returned ok=True, applicable_ids == cited_ids == [D-090-R843, D-090-R936, D-090-R937], missing_ids [], invalid_refs [], unresolved [].
 - B5: PASS. The derived applicable set across all active directives for this task is exactly those three ids, so nothing else applies uncited. Gate records: G0,G1,G2,G3,G4,G5 all PASS; G1-G5 recorded at reviewed_sha 2341590e with the same content_manifest_sha256 34461f6c... (one content identity), after the delta reviews and CI at corrected head 6c8c9f7d. CI runs 38097919683 (pull_request) and 38097916934 (push) both conclusion "success" at headSha 6c8c9f7d with zero non-success jobs (21 jobs incl. api, web, web-e2e, control-plane, contracts, modularity, both dependency-security jobs). Forbidden parent connectors (mappluto_geometry_arcgis.py, building_footprints_arcgis.py, dcm_street_centerline_arcgis.py, dcm_street_centerline_geometry.py) are byte-identical blobs at base and head; the M5-T154 material commit c322e676 touched only allowed paths. The three authorized focused tests passed: 28 passed, exit 0 (S1-S8 node ids all present and green). The schema is additive (contract_version enum ["1.0.0","1.1.0"]; context_window/tax_lots/streets optional, not in map_context.required; both schema copies byte-identical) and every 1.0.0 example still validates.

(4) CARRY-FORWARD CONDITION
 - This PASS is stamped at the frozen head 7adc476 and may be recorded at a later head WITHOUT a new review provided: (a) a blob-level predicate holds — services/api/app, services/api/tests, packages/contracts, docs/zoning-rule-review, docs/reference-cases, docs/design, apps/web/src, apps/web/e2e, apps/web/scripts, render.yaml, .github, tools, CLAUDE.md, .claude/rules and this task's reports (M5-T154-G0.md, M5-T154-reviews.md, M5-T154-evidence-map.json, M5-T154-producer-report.md) keep their blob ids; and (b) the three bound rows' text and the M5-T154 binding (applicability + verification row ids) are unchanged.
 - Tolerated later commits: those touching only project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of the sibling tasks M5-T155/M5-T156 on this branch, and a merge of the main line that changes none of the predicate files. Any product change to a predicate path, or any change to the rows' text/binding, voids this carry-forward and requires re-verification.

(5) REQUIRED CORRECTIONS
 - None. The reviewers' required corrections (code M5-T154-C1; QA C1,C2; security advisory A1) were all applied before the frozen head and I confirmed the fixes here: test_flag_off_returns_none_and_makes_no_connector_call now asserts zero connector calls with counting spies; test_manifest_lists_exactly_the_recorded_files + test_file_bytes_match_manifest_sha256 (all 3 recordings) + test_pack_has_readme_and_byte_exact_gitattributes are present and green; _resolve_inside path containment is present with test_recorded_pack_loader_refuses_a_path_escaping_the_pack. All passed in my run.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The live production path (LIVE_SPATIAL_PROVIDER_ENABLED on, real network fetch): I verified only the offline replay and the default-off gating (live_spatial_provider_enabled() False, None with zero calls); the brief forbids network, so I did not reproduce the G1 reviewer's two live keyless ArcGIS cross-checks. The flag is off by default in the shipping config.
 - The browser/Playwright rendering and the true-size print measurement (overflow n=0): produced by the orchestrator; I did not run Playwright or any server and did not touch ports 3000/3001/8000. I inspected the orchestrator-produced PDF/PNGs in print-w22g directly (pages 1-3), which match the recorded data.
 - The full api pytest suite and tools/test_directive_compliance.py: forbidden by the brief (hours-long) and are CI's job; I relied on the two green CI runs at 6c8c9f7d (read via gh, read-only) plus the validator --check exit 0 and the three focused test files.
 - The non-blocking G1 observation that, in benchmark replay only, the building-footprints source_data_last_edited (2026-09-27) is served from the reused base-pack metadata while the freshly captured footprints file's HTTP last-modified was ~2026-10-04: I confirmed the replay value (2026-09-27) but did not re-fetch live metadata; it is documented and does not affect the live provider.
 - Any human/architect/screen-reader judgement of the printed look (R938-class), which is the visual-quality-reviewer's and a person's call, not mine and not this task's bound rows.

END-OF-REPORT
````
