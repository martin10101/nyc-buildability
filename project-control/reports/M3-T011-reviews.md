# M3-T011 reviews (every return kept unchanged)

- One capture round (official-source-researcher, worktree): commit 6f49be5b integrated as the cherry-pick cebcf14c (45 files, inside the allowed paths; LF sha256 equal to the producer's return). The batch was planned by a read-only planner and corrected by a judge before contract (S10's library scope).
- G2 orchestrator self-check at the submit head: the task's files equal the producer's digests; nothing outside the allowed paths; the sync check and the bundle/law-links tests green (producer and G1); the CI run at the submit head read green before submission.
- G1 data-contract-verifier at cebcf14c: PASS, no required correction; two advisories (option-05 line 62 prose; the index's prior residuals), both disclosed by the producer and left for a later capture-state pass.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

G1 DATA-CONTRACT REVIEW — M3-T011 (data-contract-verifier). I am an AI agent, read-only; this is not a human/professional or legal review. Pinned cebcf14c on task/wave27-comparison-appendix (cherry-pick of 6f49be5b) in /root/project/w-wave20; all facts re-derived from source and the official site 2026-10-15. I did not produce this task.

VERDICT: PASS (G1). The 20 captures are genuine, faithful, integrity-clean official source text; both channels are sha256-pinned on all 20; the F1/A1/A2 lessons from M3-T010 are carried (legend quoted verbatim, correct parents, no glyph-meaning restatement); the library edits are capture-state only and match the judge's three corrections exactly. No required corrections. Two advisories, both anticipated and honestly disclosed by the producer.

WHAT I VERIFIED (all reproduced):
1. Integrity (inline script reading every object from git at cebcf14c): all 20 are zr_section_snapshot/v1; content_digest_sha256 == sha256(verbatim_excerpt) for all 20; each services/api/_zr_snapshots copy BYTE-IDENTICAL to its docs canonical; snapshot_id == filename, 20 unique; extraction_status extracted_draft; source.raw_html_verified false on all 20.
2. Loader + required checks. load_snapshot_file loaded all 20; SnapshotStore().load() resolves 255 ids with all 20 present and no duplicate-id error. Run in the live tree (the snapshot files, sync script and bundle test are byte-identical to cebcf14c; only test_report_law_links.py differs by 2 lines, an unrelated M5-T169 appendix-anchor change) under flock, lanes venv, PYTHONDONTWRITEBYTECODE=1: sync_zr_snapshots.py --check EXIT 0 ("255 file(s) byte-identical"); pytest tests/rules/test_zr_snapshot_bundle.py EXIT 0 (6 passed); pytest tests/drawings/report/test_report_law_links.py EXIT 0 (22 passed) — 28 total, matching the producer.
3. Provenance — 10 of 20 re-fetched live, one at a time, browser UA, paced (the 6 required + 22-132, 23-63, 24-39, 33-30). Every one matches the snapshot on section number, title, Last Amended, node id and body/list structure: 22-131 (22415, 12/5/2024), 74-902 (19198, 6/6/2024, canonical article-vii/chapter-4 confirmed, lettered a–d), 74-903 (19199, 3/22/2016, a/b+1–4/1–3), 24-393 (17665, 12/5/2024, a–d, 3 images), 33-303 (17752, 4/30/2008, a–c, 2 images), 35-24 (22817, 12/5/2024), 22-132 (22416, 6/6/2024), 23-63 (17505, 12/5/2024), 24-39 (17662, title-case "Other Special Provisions for Rear Yards", parent→24-36), 33-30 (17749, 12/15/1961, ALL-CAPS "OTHER SPECIAL PROVISIONS FOR REAR YARDS", parent→33-26). All 20 request_urls are official article/chapter/section pages; cross_check channel print_pdf, result "match"; no fallback needed (23-154 403 correctly deferred).
4. F1-critical legend. 22-131 carries both tables (III(A) 13 rows, III(B) 20 rows), columns Uses/R1–R12/PRC; the legend "● = Permitted  ♦ = Permitted with limitations  ○ = Special permit required  – = Not permitted  S = Size restriction  P = Additional conditions" is quoted VERBATIM and matches the live page exactly; header_structure restates no glyph meaning (A2 carried); the digest covers only the excerpt (table placeholder), so cells are HTML-canonical and disclosed. The 22-131 intro third sentence ("Notations found in the tables are further described in Section 22-10 (USE ALLOWANCES).") confirmed genuine on the live page (not invented).
5. Diagrams pointer-only. 24-393 (3 figures) and 33-303 (2 figures, printed captions "(33-303a)"/"(33-303c)" kept verbatim) carry image_url+alt_text only; no transcription, no dimension read. Matches live image filenames.
6. Nothing Verified (S5). Every "Verified" string is the ADR-007 negation or the raw_html_verified field; no rule/reading/computed number/eligibility.
7. Scope (S6). Commit touches exactly 45 files, all in allowed_paths; no forbidden path.
8. Library capture-state (S10, judge corrections). benchmark-r6b-sections.json: only 23-63/74-902/74-903 flipped captured false→true, dispositions preserved, JSON valid (A3). options-sections.md: only the 22-131..135 and 33-27/28/30 notes it carries flipped (correction #1). option-05: stale M3-T010 marks 32-421/33-26/33-301 corrected + item 5 rewritten (correction #3). option-06-07: 22-131..135 cell flipped + a labelled "capture-state bookkeeping only, not a reading" line for 24-37/38/39 (which the file names at line 96); no row added for 74-902/903 or 24-392/393 (correction #2). No reading/value changed.
9. Deferred list reported (S8): 23-154 (403), the 25-30 parking subtree 25-31..37, the 77-xx district-boundary family, 23-38/23-72 (Brooklyn), and the 12-10 "residential building" term — all in the producer report, none silently omitted.

FINDINGS
F1 — ADVISORY — option-05 line 62 prose "On which storeys shops may sit (32-421, not captured, read by HX1 live 6/6/2024)" still says "not captured" while the same file's table row and item 5 now read "32-421 CAPTURED (M3-T010)". A within-file inconsistency. The producer disclosed it and left it because it sits inside a reading paragraph (S10 scopes option-05 to lines 22/25/26 + item 5; editing a reading is out of scope). Acceptable and anticipated; a later capture-state pass should reconcile line 62.
F2 — ADVISORY — benchmark-r6b-sections.json still carries prior-task residuals outside this task's scope: 24-111 "captured": false (captured by M3-T009) and the 32-10 "NOT CAPTURED" marks. Honestly disclosed by the producer; S10/A3 scope the index to 74-902/903/23-63 only. Leave for a future pass.
(Judge advisory A4 — M4-T005's stale services/api/app/_zr_snapshots/** glob — is an orchestrator contract-time check, not a capture defect.)

WHAT I COULD NOT CHECK
- The read-only guard blocks shell file writes, so I could not extract a `git archive cebcf14c` isolated copy. I substituted by proving the relevant paths byte-identical to cebcf14c (git diff clean except the 2-line unrelated test change) and running the checks read-only in the live tree under flock — the load-bearing invariants (digest, byte-identity, loader, sync, bundle/law-link membership) are directly proven and all green.
- 10 of 20 re-fetched live (the 6 required + 4); the other 10 verified by digest/byte-identity/loader + the producer's disclosed cross-check.
- The per-requirement D-094-R102/R104 verdict is the directive-compliance-verifier's separate pass (producer ≠ verifier); my pass confirms the documents-only posture (no rule/reading/number/eligibility; nothing Verified).

Recommendation: record G1 PASS. F1/F2 are later capture-state cleanups, not blockers.

END-OF-REPORT
