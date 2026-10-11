# M5-T158 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `b54b61945e5aecd99f677b090aee60360c21471b` (branch `task/wave23-density-zoning-lot`, review copy `git plumbing at the frozen head`). Directives D-090, D-093, D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R229, R240, R241, R255, R520, R570, R584, R588, R783, R689, R007, R038, R050, R051, R057, R029, R030, R031, R032.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None for M5-T158's 19 rows. - Not a row defect but gating acceptance: the single permitted validate_directive_compliance.py --check returned INVALID (exit 1, c14 content-digest mismatch on all three directives). This is the transient/advanced-tip signature — the working tree had moved to 8cc9a3a0 where M5-T161's contracting appended task_ids mid-resync; direct frozen-head git-object computation (B2) shows the registry is internally consistent at b54b61945. It does not affect M5-T158. - Acceptance precondition (orchestrator, not a row): frozen-head CI run 38125073082 is red in ONE job only — web-e2e (results.flag-on.spec.ts expecting "special density area", caused by M5-T157, file outside M5-T158's allowed paths). The "api (ruff+pytest)" and "web (lint+typecheck+build)" jobs PASSED. Per R639 the task must not be accepted until CI is green at the accepted head; M5-T161 is the repair task. This does not change any of M5-T158's 19 row verdicts.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part (a re-dispatch: the first run was stopped at the seq-159 handoff), received 2026-10-11 08:57 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T158 (directives D-090, D-093 and D-094, 19 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent machine review of recorded evidence, NOT a human or professional legal/zoning review (ADR-007). I produced none of this work. Read-only; I wrote no file, made no commit, ran no project_control write.

(1) HEAD VERIFIED
 - I read the frozen head b54b61945e5aecd99f677b090aee60360c21471b via git plumbing in /root/project/w-wave20; its commit message records "submitted at 6b86300a; G2/G1/G3/G4/G5 PASS".
 - The branch tip has since advanced to 8cc9a3a0 (M5-T161 contracted, a disjoint-peer CI-repair task); I read every M5-T158 artifact from the frozen-head git objects, not the moving working tree.
 - Between b54b61945 and 8cc9a3a0 NO file under services/, apps/, packages/ or docs/research/evidence-records/ changed — only the 3 directives' manifest/requirements/verification (M5-T161 binding), M5-T161's packet/gate/report, and state.json.

(2) ROWS
ROW D-090-R229 — PASS
 - config.py internal_zoning_lot_index_enabled fails safe (absent/unknown -> False); classifier has the 5 states with NOT_READ when the index fails closed.
 - result_way_conditions._not_read_condition emits "could not be read … not known", never "none found"; test_db232_connector_failure_route_answers_200_with_could_not_be_read (which I ran, PASS) gets 200, exactly one such condition, and asserts "none found" absent from the whole document.
 - Nothing stays open.
ROW D-090-R240 — PASS
 - With no provider bound the state is NOT_CHECKED (config default off); test_route_body_identical_whether_or_not_index_bound asserts the study-read body is byte-identical bound vs unbound (I ran it, PASS).
 - test_db232_not_checked_adds_no_scope_row_or_condition shows NOT_CHECKED adds no scope row or figure condition; the condition never fills a figure, it marks it conditional / "Not confirmed".
 - Nothing stays open for this task.
ROW D-090-R241 — PASS
 - Benchmark values are derived from NB-01's recorded index rows (E8/E9 saved-copy sha256 MATCH the committed fixtures, verified by me) and independently reworked by G1 and G4, not from the saved fixture.
 - The journey structural guard enumerates every lot_area-sourced value with a non-vacuous counter (lot_area_values_checked>=1) and mutation proofs break->fail->restore — correctness does not rest on matching a prior snapshot.
 - Nothing stays open.
ROW D-090-R255 — PASS
 - The concern comes from the ACRIS recorded-document index (evidence), labelled draft reading DB232-R1; zoning_lot_condition uses KIND_UNCHECKED_CONDITION, never contradicted_record, and the wording says the documents "were not read".
 - NB-01 stays research_status access_blocked; no user assumption is stored or shown as a verified fact.
 - Nothing stays open.
ROW D-090-R520 — PASS
 - Journey test asserts the standard unit limit value == 29 and way == "conditional" (a conditional ceiling), unchanged.
 - It carries exactly ONE zoning-lot condition and asserts the generic "whole zoning lot" wording is absent (the property-specific one replaced it, never two); the 680/affordable-35/senior path (NB-05) is untouched, all code_identity hashes MATCH.
 - The affordable 35 / senior-none ceilings are primarily M5-T157's share; for this task the standard 29 ceiling is retained and conditional — nothing stays open here.
ROW D-090-R570 — PASS
 - Journey test asserts "39,934" and "39934" are absent from the entire document; coverage-by-portion, rear yard beyond the corner and building A stay withheld.
 - No combined lot area and no substitute number appears in a withheld slot; scope row is "Not confirmed".
 - Nothing stays open.
ROW D-090-R584 — PASS
 - The live ACRIS binding sits behind INTERNAL_ZONING_LOT_INDEX_ENABLED (default off, fail-safe); test_lane_flags covers name/posture/default-off (I ran it, PASS).
 - Production stays NOT_CHECKED and byte-identical; G5 PASS; frozen-head CI api/web jobs green.
 - The production-enablement security review (advisories, backlog DB-237) stays open but turns nothing on — nothing of this row stays open.
ROW D-090-R588 — PASS
 - The journey document still carries every option and figure (allowance, unit limit, coverage, rear yard, building A/B); the task only adds a condition, a scope row and the first open item.
 - No step narrows scope to the results screen or one option.
 - Nothing stays open.
ROW D-090-R783 — PASS
 - The affected figures each keep way == "conditional"; the scope row is "Not confirmed"; nothing new is labelled Verified.
 - The ACRIS concern adds no Verified status and establishes no conclusion.
 - The full six-label legend/mapping is M5-T151 / the PDF legend (R783 also binds M5-T151); that broader mapping stays open, not this task's share.
ROW D-090-R689 — PASS
 - NB-01 revisions 1-2 (from M0-T190) and the 2026-10-10 evidence pack are reused; revision 3 adds E8-E10 connector captures and corrects E1's URL.
 - NB-01 review history shows revisions 1/2/3 all "agrees"; research_record_check --check PASS.
 - Nothing stays open.
ROW D-093-R007 — PASS
 - No unresolved number is changed or resolved: journey asserts lot area 20,150 / 24,180, FAR 2.0 / 2.4, unit limit 29 all unchanged; zoning_lot scope stays "Not confirmed".
 - The condition only marks figures conditional; existing floor area, rear yard and unit count keep their values and states; no approval boundary changed (flag stays off).
 - Nothing stays open.
ROW D-093-R038 — PASS
 - NB-01 rev 3 E8/E9/E10 each carry authority, title, URL, reference(dataset id + builder), document_date, retrieved date, excerpt, saved_copy and sha256; saved copies live in the benchmark fixture folder.
 - E8/E9 saved-copy sha256 MATCH the committed fixture bytes (I recomputed both); NB-05 rev 3 was added (scope correction 2) for the three moved code files; research_record_check --check PASS (6 records current).
 - Nothing stays open.
ROW D-093-R050 — PASS
 - NB-01 rev-3 agent_review (data-contract-verifier, verdict "agrees") records opening the primary sources, working the connector+classifier result before reading code, and a read-only live confirmation that the official Legals still indexes ZONE 2022020201551002 against lots 1 and 70.
 - NB-05 rev-3 was delta-reviewed (agrees); the review report is project-control/reports/M5-T158-reviews.md.
 - Nothing stays open; professional review remains advisory/null by design.
ROW D-093-R051 — PASS
 - Changed logic is tested at boundaries not by formula copy: per-state emit tests (NOT_READ, NONE_FOUND, SINGLE_LOT_ONLY, another-block), partial_lot P, mixed document, every connector failure path, NOT_CHECKED identity (33 profile/connector tests + 99 journey/emit/wiring/flag tests passed when I ran them).
 - The recorded benchmark is labelled recorded and synthetic fixtures are labelled synthetic; builder and G4 supplied mutation proofs.
 - Nothing stays open.
ROW D-093-R057 — PASS
 - NB-01 observed_facts list the CERT/ZONE/DECL (CRFNs 2022000059133/59134/121661) as index entries only; the ZONE/DECL/CERT fixtures confirm lots 1 and 70 same block; status is access_blocked (instruments unread).
 - The program states that index-only concern on every lot-area figure and never concludes the zoning lot.
 - Nothing stays open.
ROW D-094-R029 — PASS (for this task's share)
 - Journey test asserts 20,150 carries the condition naming "lot 1", "February 8, 2022" and settled_by "2022000059134", with way "conditional"; building B carries the marker too.
 - report_pages test_db232_zoning_lot_open_item_is_first asserts the first open item is "Zoning lot" (number 1, reason names lot 1) — prominence near the headline (I ran it, PASS).
 - OPEN: the exact page-1 headline summary sentence rewording is the redesign task P-3 (page_decision_summary.py is out of this packet's allowed paths).
ROW D-094-R030 — PASS
 - The generic unit-limit condition is replaced by the property-specific one (journey asserts "whole zoning lot" absent); the scope row, first open item and figure conditions are new property-specific treatments, so the generic sentence is no longer the only treatment.
 - The condition marker "register of recorded documents" distinguishes it from the generic sentence.
 - OPEN: the page-1 generic summary sentence itself remains until P-3 replaces it (acknowledged in the evidence map), but the row's requirement — no longer the only treatment — is met.
ROW D-094-R031 — PASS
 - NB-01 rev 3 keeps the evidence pack's distinctions: index facts in observed_facts, draft reading DB232-R1 in interpretation, unread instruments as access_blocked.
 - The October-10 evidence pack and its saved copies are reused and digest-matched.
 - Nothing stays open.
ROW D-094-R032 — PASS
 - Journey asserts "39,934"/"39934" absent everywhere; no remaining-capacity figure is computed by subtracting lot 1 from the DOB field.
 - Remaining capacity stays "Not confirmed"; no replacement figure is established.
 - Nothing stays open.

(3) BINDING B1–B5
 - B1: contract commit 5b81aeee appended only "M5-T158" to task_ids of exactly the 10 D-090, 5 D-093 and 4 D-094 rows plus updated_at; no requirement text changed (line-level diff reviewed).
 - B2: at the frozen head, each manifest's requirements_content_digest_sha256 equals sha256_text_artifact(requirements.json) computed over the git-object bytes (D-090 160eac…, D-093 d6c314…, D-094 3c4468…) — all MATCH.
 - B3: each directive's verification.json has exactly one M5-T158 row, verifier "", schema v2, with the cited requirement ids all state "pending".
 - B4: exactly 19 rows bind M5-T158 and they equal the packet's cited directive_refs (applicable == cited).
 - B5: a scan of ALL directives at the frozen head finds M5-T158 bound in only those 19 rows (nothing uncited applies); gate records G0 PASS (at 55c2d745) and G1/G2/G3/G4/G5 PASS at one content identity (6b86300a, manifest 0277de79).

(4) CARRY-FORWARD CONDITION
 - Blob-level predicate HOLDS now: every M5-T158 allowed-path file (code, tests, fixtures, NB-01, NB-05, records) is byte-identical between b54b61945 and the current tip 8cc9a3a0, and all 19 rows keep their text and M5-T158 binding.
 - My PASS may be stamped at a later head provided those allowed-path blob ids and the 19 rows' text + M5-T158 binding are unchanged there.
 - Broad disjoint-peer tolerance applies: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/ including other evidence records, their packets/gates/reports, other tasks' directive bindings, ledger state), this task's own acceptance records, and a main-line merge changing none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None for M5-T158's 19 rows.
 - Not a row defect but gating acceptance: the single permitted validate_directive_compliance.py --check returned INVALID (exit 1, c14 content-digest mismatch on all three directives). This is the transient/advanced-tip signature — the working tree had moved to 8cc9a3a0 where M5-T161's contracting appended task_ids mid-resync; direct frozen-head git-object computation (B2) shows the registry is internally consistent at b54b61945. It does not affect M5-T158.
 - Acceptance precondition (orchestrator, not a row): frozen-head CI run 38125073082 is red in ONE job only — web-e2e (results.flag-on.spec.ts expecting "special density area", caused by M5-T157, file outside M5-T158's allowed paths). The "api (ruff+pytest)" and "web (lint+typecheck+build)" jobs PASSED. Per R639 the task must not be accepted until CI is green at the accepted head; M5-T161 is the repair task. This does not change any of M5-T158's 19 row verdicts.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run the full api suite or the web-e2e suite (forbidden); I relied on the frozen-head CI "api (ruff+pytest)" PASS plus my own focused offline runs — classifier/connector (33 passed), journey/emit/wiring/flags (99 passed), results-read + report-pages db232 (8 passed) — all on files proven byte-identical to the frozen head.
 - I did not open the live ACRIS datasets (no network; records are access_blocked by design). I verified the saved-copy sha256 against the committed fixtures and relied on G1's recorded 2026-10-11 live confirmation that the ZONE still names lots 1 and 70.
 - The draft reading DB232-R1 is unreviewed by a professional (advisory, ADR-007); I verified only that it is labelled a draft and never concludes the zoning lot.
 - The single validator run reflected the advanced tip (8cc9a3a0), so for the frozen head I substituted direct git-object digest computation as the authoritative B2 evidence.
END-OF-REPORT
```
