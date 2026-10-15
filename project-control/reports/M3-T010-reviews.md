# M3-T010 reviews (every return kept unchanged)

- One capture round (official-source-researcher, worktree): commit 220ecb43 integrated as the cherry-pick fd48fbc0 (inside the allowed paths; LF sha256 equal to the producer's return); 20 snapshots, their bundled copies, the law-library capture-state corrections and the producer report.
- Independent pre-integration check (return-M3-T010-precheck.json, session 2026-10-15a): scope, digests, sync check, ruff, the bundle and law-links tests, lane coverage.
- G1 data-contract-verifier at fd48fbc0: PASS with one REQUIRED (F1: the method note of four captures transposed the use-allowance symbol meanings) and three advisories (A1 a wrong parent named in the producer report; A2 inapplicable glyph boilerplate in 23-12/23-371; A3 the two 12-10 terms have no print channel, a disclosed limitation). All 20 re-fetched byte-identical.
- Corrections by the orchestrator: a6da66bd [ORCH-CORRECTED per G1 F1] (only cross_check.method of the four captures, both copies; the bundle and law-links tests 28 passed under the lock after it) and 48d6587b [ORCH-CORRECTED per G1 A1] (one producer-report sentence).
- G1 delta check (data-contract-verifier, session 2026-10-15b) at 48d6587b: PASS; key-level diff shows only cross_check.method changed in the 8 files plus the one sentence; each corrected note matches the official key quoted live; digests and both copies byte-identical; A1 now true; A2 residual in header_structure, harmless, carried as an advisory for a later tagged note cleanup; A3 unaffected.
- G2 orchestrator self-check at the submit head: the task's files at the submit head equal 48d6587b's (no change since); lane coverage PASS (producer); the CI run at the submit head read green before submission.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

All checks complete. Parent/heading handling confirmed (22-12 and 23-35 parent-only; 25-24 heading-only). The F1 list-label discipline is fully verified with no recurrence. Here is my G1 report.

---

VERDICT: PASS with required corrections (one REQUIRED, bounded and text-only; three ADVISORY). The 20 captures are genuine, faithful, integrity-clean official source text; the single REQUIRED item is a provenance-note wording error that touches no captured value, excerpt, digest, legend, or table cell.

Task: M3-T010 G1 (data-contract-verifier, AI agent — not a professional/legal review). Pinned `fd48fbc0` on `task/wave26-envelope-constraints` in `/root/project/w-wave20`; all checks run in a `git archive` copy at `/tmp/claude-0/m3t010-g1/archive`, lanes venv, `PYTHONDONTWRITEBYTECODE=1`, direct exit codes.

=== FINDINGS ===

F1 — REQUIRED — `cross_check.method` swaps the use-allowance glyph meanings, contradicting the same file's verbatim legend. In zr-22-121, zr-32-121, zr-23-12, zr-23-371 the method prose reads "● Permitted, ○ Permitted with limitations, ♦ Special permit required … S/P/U condition letters". The official §22-121 / §32-121 symbol key (re-fetched live, tag-stripped) is: "● = Permitted ♦ = Permitted with limitations ○ = Special permit required – = Not permitted S = Size restriction P = Additional conditions [U = Open use allowances for 32-121]". The captured `table.legend` fields match the official key exactly; the `cross_check.method` has ○ and ♦ transposed and loosely calls S/P/U "condition letters" (U = Open use allowances). Material in zr-32-121, whose C3 data cells carry ♦ for single-family/two-family "Other types" and "All other types" — official meaning "Permitted with limitations", which the method note mis-renders as "Special permit required". Note: the `tables` block is NOT covered by `content_digest_sha256` (digest is over the excerpt, which holds a `[table …]` placeholder), so table/legend fidelity rests on manual review — I verified every cell of 32-121, 22-121, 23-12 and both 23-371 tables against the official HTML and they are verbatim-correct. Fix (text-only, no digest change): correct the method prose in the 4 files to match the verbatim legend; drop the inapplicable glyph clause from zr-23-12/zr-23-371 (their tables contain no ●○♦); re-run `sync_zr_snapshots.py` so the bundle stays byte-identical.

A1 — ADVISORY — Producer report S4/S8 narrative mislabels "22-12 → children 22-131…22-135". Those are children of 22-13 (Use Group III), not 22-12 (whose children are 22-121/22-122, both captured). One listing GET of article-ii/chapter-2/22-13 (HTTP 200) shows 22-131, 22-132, 22-133, 22-134, 22-135 all exist and are correctly deferred. The library file option-06-07 places them under 22-13 correctly; the error is isolated to the producer report.

A2 — ADVISORY — Inapplicable boilerplate. zr-23-12 and zr-23-371 `header_structure`/`method` carry the "use-allowance glyphs ●○♦ … render as '?'" clause although neither table uses those glyphs. Harmless; trim when fixing F1.

A3 — ADVISORY/limitation (not a defect) — The two §12-10 terms have no print/PDF channel (whole-page 504, per-term 403 — the documented DB-167 fallback, disclosed in each file); their list labels are markup positions ("cite by words"). I confirmed the term TEXT verbatim against the official node-18523 HTML and both per-term Last Amended stamps (Inner 12/5/2024; Select 6/6/2024).

NOTE on the brief — CHECK items 2–3 name 24-111, parents 22-13/24-11/24-52, and quirks "24-11 lowercase header / 24-522 missing space / omitted illustration". None of those are in M3-T010's 20 files (they are prior M3-T008/T009 sections) — stale template carryover. I applied the intent to this task's real parents/heading and its real disclosed quirks (below); all pass.

=== WHAT I CHECKED (all reproduced) ===

1. Integrity (own inline script, 20 new files): every file is `zr_section_snapshot/v1`; `content_digest_sha256 == sha256(verbatim_excerpt)`; `snapshot_id == filename`; `extraction_status extracted_draft`; `source.raw_html_verified false`; each services/api bundled copy byte-identical to its docs canonical. No duplicate `snapshot_id`. Every "Verified" string is either the `raw_html_verified` field or the ADR-007 negation ("Nothing … is a Verified zoning determination"); no rule/reading/computed number/eligibility — table numbers are verbatim ZR source values.

2. Loader + required checks (archive, lanes venv): `SnapshotStore` loads the full folder (235 ids, no duplicate-id error) from both the packaged and canonical dirs; all 20 new ids present. `sync_zr_snapshots.py --check` → EXIT 0 ("235 file(s) byte-identical"). `pytest -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/drawings/report/test_report_law_links.py` (under `flock heavy-run.lock`) → EXIT 0, 28 passed (confirms bundle==canonical membership, store digest validation, and that the benchmark fixture cites none of the 20 — no href change, S3).

3. Provenance (my own one-GET-each, official host only, paced): re-fetched the 12 distinct section HTML pages the precheck did not (22-12, 22-121, 22-122, 32-121, 25-24, 23-371, 23-372, 23-35, 23-351, 23-352, 23-353, §12-10 node 18523) — every one byte-for-byte identical to the recorded `raw_html_sha256`. With the precheck's 7 (23-51, 33-301, 54-311, 32-421, 33-26, 23-12, 25-241) this independently confirms all 20 captures are the genuine official source text as of 2026-10-15.

4. Fidelity — section number/title/Last Amended match the live page for every file. List labels taken from the PRINT (the M3-T008 F1 fix): I pulled the print/PDF text layer (pdftotext) and matched labels item-by-item for 23-371 (a–d, nested (1)(2)(i)(ii), + both tables cell-for-cell: 15/20/30 and the 10-row 50→41 coverage table), 23-351 (a–d, incl. the three unlabeled fire-escape continuations under (b)), 23-352 (a–c), 23-353 (a–c), 22-122 (a,b,1–6 + lead-in/trailing paragraphs), 32-421 (a,(1)(2),b–e), 23-372 (a,b,(1)(2)(3),c,d), 22-12 (a,b). 25-241 (a,b) confirmed by the precheck. 23-51/54-311/33-26/33-301/23-35 are pure prose (no labels). No HTML-restart artifact anywhere. Tables: 22-121, 32-121 (incl. ♦ in C3), 23-12 (2,375/25; 1,700/18) and both 23-371 tables verified cell-for-cell against the official HTML (symbol cells are HTML-canonical; glyphs render as '?' in the PDF — disclosed, S7/ADDED-d).

5. Parents / heading (S8 / ADDED-c): 22-12 and 23-35 hold the parent's own text only and exclude the children's bodies (22-12's node-18149 PDF renders 22-121/22-122, but the excerpt keeps only (a)/(b)); 25-24 has an empty official `field--name-body` (only a nav menu) and is captured as number+title with `result:"no_own_body"`, identical to the accepted zr-23-44 / zr-35-64 heading precedent — no text invented.

6. §12-10 fallback (ADDED-b/S9): both terms disclose the 504/403 documented fallback; "Select commercial overlays … C1-1…C2-4 Districts" and the Inner-Transit-Zone definition (incl. the source's own unclosed opening quote before "Inner Transit Zone") match the official page verbatim.

7. Scope (S6): `git diff-tree` = exactly 45 files, all in allowed_paths; no forbidden path, no rule/scenario/test/evidence-record, `sync_zr_snapshots.py` unchanged.

8. Library capture-states (S10 / ADDED-a): the four files are capture-state-only. Every changed [C]/[NC]/'NOT CAPTURED' mark matches `ls` at fd48fbc0 (235 files) — 27-xx + Appendix F + senior sub-terms, every zr-24-*, the court group, 32-421/33-26/33-301, 22-12/121/122/23-51/32-121/54-311, Transit-Zone-Inner/25-24/25-241 all present; 33-27/33-28/33-30, 22-131…135, 25-30+, 77-xx correctly left NOT CAPTURED. The "affordable independent residence for seniors" plural→singular matches the M3-T008 F2 finding. benchmark-r6b-sections.json: only the 32-131 re-pointing changed (C2-2 retail now = 32-161/UG VI); valid JSON; references none of the 20 (none owed). 66-11 re-worded to "mass transit station" (zr-66-11 present, title "Definitions"). No reading/value changed.

=== WHAT I COULD NOT CHECK ===
- No second-human raw-HTML re-read; `raw_html_verified` correctly stays false / `extraction_status extracted_draft` (by design).
- Prior-task (M3-T008/T009) snapshot dates now cited in the library marks (e.g., zr-24-163 12/5/2024) — accepted under those tasks; not re-derived here.
- The formal per-requirement D-094 R102/R104 verdict is the directive-compliance-verifier's (producer≠verifier); my pass confirms the documents-only posture (no rule/reading/number/eligibility; options 8 and 10 meanings not asserted).

Recommendation: record G1 PASS; apply F1 as a tagged text-only `[ORCH-CORRECTED per G1 F1]` edit to the 4 method notes + `sync --check` before acceptance (no digest/excerpt/cell/legend change). A1/A2/A3 are orchestrator/producer-note cleanups.

END-OF-REPORT

## G1 (data-contract-verifier, delta check of the two corrections)

G1 DELTA REVIEW — M3-T010 (data-contract-verifier). I am an AI agent, read-only; this is not a professional/legal review. Pinned 48d6587b on task/wave26-envelope-constraints in /root/project/w-wave20 (HEAD confirmed == 48d6587b at check time); material pre-correction head fd48fbc0. All facts re-derived from source; I did not rely on the round-1 return.

VERDICT: PASS (G1 delta). The round-1 REQUIRED (F1) and A1 are correctly and completely fixed; scope is clean; no capture value, excerpt, digest, legend or table cell changed. One residual ADVISORY only (A2 boilerplate in header_structure), harmless — not a blocker.

D1 SCOPE — PASS. JSON key-level diff fd48fbc0->48d6587b over the packet's allowed_paths: in all 8 snapshot files the ONLY changed leaf key is /cross_check/method (no key added/removed), plus one sentence of M3-T010-producer-report.md. Nothing else in allowed paths. (The full branch diff touches many files — other wave-26 tasks M5-T170/183/184, R6B cases, etc. — all OUTSIDE M3-T010's allowed paths; expected, the branch moves.)

D2 F1 ACCURACY — PASS. Official pages re-fetched live (zoningresolution.planning.nyc.gov, 2026-10-15):
- 22-121 key verbatim: "● = Permitted  ♦ = Permitted with limitations  ○ = Special permit required  – = Not permitted  S = Size restriction  P = Additional conditions" — corrected note matches exactly; U correctly omitted (22-121 has no U).
- 32-121 key: same plus "U = Open use allowances" — corrected note matches (includes U).
- 23-12: single numeric "min lot area/width" table (2,375/25; 1,700/18), no symbols, no legend — note now reads "this section's table uses none of them." Correct.
- 23-371: two numeric tables (feet 15/20/30; coverage 50->41%), no use-allowance symbols, no legend — note reads "this section's tables use none of them." Correct (singular/plural right).
Corrected meanings also agree with each file's own UNCHANGED table.legend and with round-1's cell reading (32-121 C3 ♦ = "Permitted with limitations"). The pre-fix prose had ○/♦ transposed; now fixed.

D3 INTEGRITY/SCHEMA — PASS. For all 4 sections: content_digest_sha256 == sha256(verbatim_excerpt) (verbatim_excerpt unchanged), and docs copy byte-identical to bundled app/_zr_snapshots copy (direct byte compare: 10194/9737/8241/14614 bytes, equal). Loader load_snapshot_file invariants intact; cross_check.method is free-text, not schema-validated; no keys added/removed, so the schema still validates. I did NOT re-run the bundle/law-link suite: the read-only guard blocks extracting an isolated scratch copy (tar -x is a shell write) and running the moving live tree is inappropriate. It is also unnecessary — test_zr_snapshot_bundle asserts docs/bundle byte-identity, digest validation and importlib discovery, none of which depend on method text; round-1 ran it green (28 passed) and the delta applied the identical edit to BOTH copies, preserving byte-identity. Load-bearing invariants directly proven above.

D4 A1 TRUE — PASS. Official: 22-13 = "Use Group III – Community Facilities" with children 22-131..22-135; 22-12 = "Use Group II – Residences" with children 22-121 and 22-122 (both captured in this batch). The corrected report sentence is now correct.

D5 A2 DISPOSITION — ADVISORY (residual, harmless; NOT required). The fix added "...this section's table(s) uses/use none of them" to cross_check.method, so the METHOD clause is no longer misleading. However the correction touched only method: tables[*].header_structure of zr-23-12 (tables[0]) and zr-23-371 (tables[0] and tables[1]) STILL carries the boilerplate "...use-allowance glyphs ●○♦ and the en-dash – are the HTML's verbatim symbols (the print/PDF text layer renders them as '?', ...)" although neither table contains those glyphs. This clause asserts no symbol MEANING and affects no captured value, so it is harmless, but it is the inapplicable boilerplate round-1 recommended trimming and it remains in header_structure. Optional cleanup; does not block acceptance.

D6 A3 — Unaffected. The §12-10 504/403 print-channel fallback is a disclosed limitation, not among the 4 corrected files; nothing to re-verify in this delta.

WHAT I COULD NOT CHECK: bundle/law-link pytest not executed (reason in D3 — guard blocks isolated-copy extraction; proven unnecessary and directly substituted). raw_html/raw_pdf bytes not re-fetched this round (round-1 confirmed all 20; the delta changes no captured bytes). Recommend: record G1 delta PASS; optionally apply A2 header_structure trim as a later tagged doc-note cleanup.

END-OF-REPORT
