# M0-T197 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `e10c674505bfb97ff4e96a6bcdec99f05b42de67` (branch `task/wave29-scenario-drawings`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R058, R060, R098, R150, R265, R285.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None blocking M0-T197's share: all six rows PASS for this task's contribution; both material commits are in-scope; hygiene is green (29-test self-test OK, test_project_control.py 25 groups OK, test_directive_reminder.py 22 tests OK, validator exit 0, CI 21/21). - Directive-level flag (not a code correction to M0-T197): R150 is an obligation whose substance — producing the corrected 2026-10-14 comparison document from each revision's running build and sending it to the owner — is NOT delivered by this task, and R150's applicability lists only D-094-BOOTSTRAP and M0-T197. Before D-094 can be called complete the orchestrator must bind/own that corrective+send deliverable to a task that actually performs it; M0-T197 only supplies the E4 detection guard. - Advisory to carry (not blocking): report_export_check.py is in the modularity JUSTIFY band at 841 source lines (modularity_check --check exits 0, report-only; recorded cohesion justification; backlog DB-292) — schedule a facade split via a new allowed path before further growth.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-16 02:05:48 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T197 (directive D-094, 6 bound rows)
VERDICT: PASS

NOTE ON ROW COUNT: the brief's return-header template says "9 rows", but the packet's directive_refs, verification.json, and evaluate_task_refs all show exactly 6 bound rows (R058, R060, R098, R150, R265, R285). I report the verified count (6); the "9" in the template is a stale artifact, not a binding I could find.

(1) HEAD VERIFIED
 - I read the frozen head e10c674505bfb97ff4e96a6bcdec99f05b42de67 on branch task/wave29-scenario-drawings via git plumbing in /root/project/w-wave29.
 - The worktree HEAD has since advanced to b561450ef35150cad2da607a91ac08e5b3e37683; I confirmed e10c6745 is an ancestor of it (git merge-base --is-ancestor = YES) and that the only files changed across that span are disjoint peers: the directive manifest/requirements/verification, master_plan.json, and the new M5-T173.json packet.
 - The three task files keep identical blob ids at c4422294 (gate-reviewed), e10c6745 (frozen), and b561450e (current): report_export_check.py 73118b95, test_report_export_check.py 94dfa702, producer-report.md eaeb0537; and none of the self-test's product inputs changed e10c6745..b561450e, so my test runs faithfully reflect the frozen head.

(2) ROWS

ROW D-094-R058 — PASS
 - Owner text (source-001.md line 175) "each result and diagram comes from the same result revision and scenario; ... allowance, scheduled area, demonstrated site fit, preliminary apartment estimate and legal unit limit stay distinct" is served by rule A4 + the C family; I read the quote in the source and the row text sha matches.
 - A4 (report_export_check.py:551-553) recomputes document_fingerprint over the results with per-run metadata excluded (exclusion tuple parsed from the product's services/api/app/drawings/report/run_identity.py text, load_repo:464) and compares it to the printed "document fingerprint:"; I reran test_a_value_change_changes_the_fingerprint, test_per_run_metadata_does_not_change_the_fingerprint and test_matches_product_and_exclusion_parsed (import app) — all ok.
 - C4 (rules_c:739-751) keeps bases distinct: it FAILs a reconciled midpoint of two distinct-basis figures and a swapped basis label; I confirmed from the primary source that docs/reference-cases/R6B/cases/placement-building-b.json carries the settled figures (tax 33.34, GIS 35.31, recorded 10,075, measured 10,387.99) and drove _basis_values live to get clearance {tax:33.34, gis:35.31}, pairs [(33.34,35.31),(10075.0,10387.99)] — no product constant.
 - Stays open: the check is a tool run on each final export (M0-T195); it does not itself change the report, so nothing in the report is altered by this task.

ROW D-094-R060 — PASS
 - Owner text (source-001.md line 177) "open the actual PDF evidence links and check destinations; internal references such as 'item 3' get a precise page or anchor destination" is served by rule D3 (_links:863-888); row text sha verified against source.
 - D3 opens the PDF link annotations, resolves each href #anchor against pdf.dests (FAIL on a missing destination), maps "see item N" to an issue-N anchor, and reports a compressed-object-stream PDF as REVIEW (never PASS); I reran test_object_streams_review_links — ok.
 - Stays open: the live --fetch-links network path to verify external URL destinations exists (_fetch:890-896) but was not exercised in review and is not run here (network); actual external-destination fetching happens only when M0-T195 runs the tool with --fetch-links on a real bundle.

ROW D-094-R098 — PASS
 - Owner text (source-003-amendment.md line 32) "the rendered result is checked for readability and consistency before the work is called complete" is served by the B family measuring drawn geometry; row text sha verified.
 - B1/B5/B6 measure the DRAWN geometry (rect w*h and absolute-M/L/Z shoelace: _shape_area:256, _path_area:269, _area_ratio:616), not a stamped attribute: a 0.898 drawn apartment ratio against a 0.60 share FAILs, and unmeasurable geometry returns REVIEW (never PASS); I reran test_drawn_zone_geometry_0898_fails_b5 and test_unmeasurable_zone_path_is_review_not_pass — ok, and read _zones:654-686 to confirm the authoritative check is the measured ratio.
 - D5 and the D6 overlap/dark-pixel sub-checks are surfaced as explicit OWED lines (rules_d) rather than silently absent; my S1 run printed "D5 OWED", "D6 OWED", "D6 REVIEW" with every other rule PASS and the suite exits 3, never a silent all-green 0.
 - Stays open: readability-by-eye stays with the human/visual reviews; full D5 (figure/caption page attribution) and the D6 overlap/dark-pixel sub-checks are owed refinements (backlog DB-292), correctly reported OWED/REVIEW.

ROW D-094-R150 — PASS (for this task's share only; the substantive obligation is NOT this task's deliverable)
 - Owner text (source-021-amendment.md line 26) is a full obligation: correct the 2026-10-14 comparison document whose page-6 before/after screenshots are one duplicated image, show genuine pictures from each named revision's running build scrolled to the changed part, state plainly the first screen is unchanged, and send the corrected file to the owner; row text sha verified and classification is "obligation".
 - This task's contribution is ONLY rule E4 (rules_e:962-968): it labels a before/after picture pair "unchanged" solely when the sha256 digests are equal, else "changed"; I reran test_before_after_unchanged_only_on_equal_digests — ok. E4 is a sound regression guard against exactly the duplicate-picture defect.
 - M0-T197 does NOT itself produce or send a corrected comparison document; it changes no product/report/record file (material commits touched only the 3 allowed tool/report paths).
 - Stays open (material): the actual corrected comparison document, captured from each revision's running build and sent to the owner, is not delivered by this task; R150's applicability currently lists only D-094-BOOTSTRAP and M0-T197, so the orchestrator must confirm which task/comms step owns producing and sending that corrected file (see REQUIRED CORRECTIONS).

ROW D-094-R265 — PASS
 - Owner text (source-028-amendment.md lines 276-278) "tests render the report and check claims against what is drawn" (because passing tests did not catch the audited contradictions) is served by the S2 real-head integration tests; row text sha verified.
 - On the rendered audited head 8fbf701b the tool reports B1 FAIL and B5 FAIL (the audited contradiction: footprint/zones claimed, none drawn); on the honest head b7f47369 it reports B3/B7 OWED with no B1/B5 FAIL; I reran test_audited_head_fails_b1_and_b5 and test_honest_head_is_owed_not_failed against the real pinned prints in session-2026-10-15c/check-fixtures — both ok.
 - The S1 synthetic bundle is rendered end-to-end (report.html printed to report.pdf by apps/web/scripts/print-report-pdf.mjs, a one-shot headless-Chromium render, no server/port) and every rule inspects the rendered PDF/HTML; I reproduced the full 29-test self-test green under the heavy-run lock.
 - Stays open: the "integration coverage" is the tool itself, meant to be run on each final export (M0-T195); CI does not run tools tests (by design for this task), so the standing evidence is the self-test under the lock.

ROW D-094-R285 — PASS
 - Owner text (source-028-amendment.md line 307) "missing values remain missing rather than becoming zero, and conditional results remain conditional: in print and website" is served by rules C5/C6; row text sha verified and classification is "prohibition".
 - C5 (rules_c:757-768) FAILs a nan/inf/infinity token in print OR website text, and FAILs a null/absent result value (results value is JSON null, _dig2 == (True, None)) rendered as "0"/"0.0"/"0.00", while a legitimate zero passes; I reran test_nan_in_text_fails_c5, test_null_rendered_zero_fails_c5 and test_legitimate_zero_passes — all ok.
 - C6 (_options:808-813) keeps the not-evaluated option rows accounted (counts the 11 rows; test_option_count_fails_c6 ok), so conditional/option rows are not silently dropped.
 - Stays open: the print side (null-vs-zero, non-finite tokens) is fully served; the website HTML row-content check that "conditional stays conditional" on the site is an owed refinement (DB-292) — E1 only checks website layout — so the website half of this row is partly owed.

(3) BINDING B1–B5
 - B1 PASS: the contract commit 2606b85e appended "M0-T197" to exactly the six rows' applicability.task_ids (6 added lines; the parent 2606b85e~1 lacked it in all six); the task's material commits c1ac389f and accd28cb touched only the three allowed paths, so no row text was changed by this task; the six rows' text sha256 are byte-identical at e10c6745 and at current HEAD b561450e.
 - B2 PASS: I recomputed sha256 over the normalized (LF) bytes of requirements.json at e10c6745 = 4d6b292328bda425bc6395421e130e527c8732defbec5e96af8f137f9f7d6955, which equals the manifest's requirements_content_digest_sha256 (raw == normalized; the file is LF).
 - B3 PASS: verification.json at e10c6745 has exactly one M0-T197 task_verifications row, applicable_requirement_ids = the six ids, producer backend-engineer, verifier "" (empty), every requirement pending with empty evidence; it was written in the same contract commit 2606b85e as requirements.json + manifest.json (c14 satisfied).
 - B4 PASS: registry.evaluate_task_refs(M0-T197) = {ok:True, applicable_ids == cited_ids == the six, missing_ids:[], invalid_refs:[], unresolved:[]}.
 - B5 PASS: missing_ids empty means nothing applicable-but-uncited across active directives; validate_directive_compliance.py --check returned exit 0 at the live head; and CI run 38836291821 at c4422294 shows the control-plane (ADR-005 workflow regression) job success, corroborating the registry integrity. Gates: G0 PASS (orchestrator, reviewed_sha 2606b85e), G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer), the latter three all at content identity c4422294 (content_manifest_sha256 4a1d03c0716d8956e70684de0dce43e76c3d01d788ffd3b82336bd437365ae06); M0-T197-reviews.md holds G3 round-1 (PASS with one required correction) + G3 round-2 delta (PASS) and G4 round-1 (FAIL, four required items) + G4 round-2 delta (PASS, each round-1 item reproduced closed); task files byte-identical c4422294 -> e10c6745; CI 21/21 jobs success at c4422294.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later accept head WITHOUT a new review while a blob-level predicate holds: tools/report_export_check.py == blob 73118b95, tools/test_report_export_check.py == blob 94dfa702, project-control/reports/M0-T197-producer-report.md == blob eaeb0537; AND the six rows (R058, R060, R098, R150, R265, R285) keep their current text (sha unchanged) and their M0-T197 applicability binding.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file — other tasks' sources under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports; other tasks appended to the applicability of these same rows (e.g. the wiring part M5-T173 at its contract, with its digest resync and provisional rows — already present at b561450e and verified harmless); new rows appended to the directive; ledger/master_plan/verification state — plus this task's own acceptance records and a merge of the main line that changes none of the predicate's files.
 - I verified this tolerance empirically: the span e10c6745..b561450e already includes M5-T173's contract (requirements/manifest/verification resync + new packet) and the three task-file blobs and all six row shas are unchanged, and the validator still exits 0.

(5) REQUIRED CORRECTIONS
 - None blocking M0-T197's share: all six rows PASS for this task's contribution; both material commits are in-scope; hygiene is green (29-test self-test OK, test_project_control.py 25 groups OK, test_directive_reminder.py 22 tests OK, validator exit 0, CI 21/21).
 - Directive-level flag (not a code correction to M0-T197): R150 is an obligation whose substance — producing the corrected 2026-10-14 comparison document from each revision's running build and sending it to the owner — is NOT delivered by this task, and R150's applicability lists only D-094-BOOTSTRAP and M0-T197. Before D-094 can be called complete the orchestrator must bind/own that corrective+send deliverable to a task that actually performs it; M0-T197 only supplies the E4 detection guard.
 - Advisory to carry (not blocking): report_export_check.py is in the modularity JUSTIFY band at 841 source lines (modularity_check --check exits 0, report-only; recorded cohesion justification; backlog DB-292) — schedule a facade split via a new allowed path before further growth.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The live --fetch-links network destination fetching for external URLs (network path, not run in review or by me).
 - The substantive R150 deliverable (a corrected comparison document created and sent to the owner): it is outside this task's three files and I did not verify it was produced or sent.
 - Full D5 (figure/caption page attribution) and the D6 overlap/dark-pixel and C6 HTML-row content checks: these are owed-and-unimplemented by design (correctly surfaced OWED/REVIEW), so I could only confirm they are honestly reported as owed, not that they work.
 - Per-source digest matching for all 32 source-*.md files: I recomputed the requirements.json digest directly and relied on the validator (exit 0) and the CI control-plane job for the source-digest set; I did not hand-recompute each source digest.
 - Windows behavior: not applicable/not run (stdlib tool on a Linux host; no CRLF in play).
 - Downstream M0-T195 consumption of the tool and how it will invoke it on the final candidate (declared out of scope by the packet).
 - I executed the self-test at current HEAD b561450e rather than literally checking out e10c6745; I mitigated this by proving the three task files and all six row shas are byte-identical across e10c6745/c4422294/b561450e and that no self-test product input changed in that span.

END-OF-REPORT
```
