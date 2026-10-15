# M3-T009 reviews (every return kept unchanged)

- G2 orchestrator self-check: the researcher's commit integrated as ccf8e24b (cherry-pick of da377afb); every file inside the packet's 31 allowed paths; LF sha256 equal to the producer's return; lane coverage PASS.
- G1 data-contract-verifier at ccf8e24b: PASS, no required finding; three advisories (five node ids not confirmed directly; the special-permit glyph; the rule-check row belongs to the directive-compliance verifier).

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

<!-- saved unchanged by save_return.py from agent-a1487941f7c9361f3.jsonl, entry 2026-10-14T20:24:34.009Z, sha256 0c2aa9c875d733c285a4258128104130e63680962afe7a1b2c5dd24ad2323a2d -->
G1 REVIEW — M3-T009 (fifteen community-facility ZR source-text captures: 22-13 + Article II Ch 4) — independent, read-only (data-contract-verifier, an AI agent; not a professional/legal review).

Pinned commit ccf8e24be7870e1e0c02ef97eaa15d2485a2ba85. The task branch moved during review (HEAD now 0f7d6364); I read the exact pinned content with `git show ccf8e24be:<path>`. Shell file-writes are blocked for my role, so I could not create a `git archive` copy; instead I proved all 34 task-relevant files (15 canonical + 15 bundle + sync script + loader + the two test files) are byte-identical at ccf8e24be vs the clean worktree HEAD (`git diff ccf8e24be HEAD` = 0 lines each; working tree clean) and ran the required suites in the worktree — a faithful reproduction of the frozen content. Web checks used the official host only (HTML + print/PDF), gently; PDFs were read via the saved binaries.

VERDICT: PASS. No required defects. Three ADVISORY/limitation notes below. The one required fix from the previous set (M3-T008 G1 F1: list letters taken from HTML markup instead of the print) is checked for again on EVERY lettered list and is handled correctly here.

=== WHAT I CHECKED (all reproduced) ===

1. Shape/integrity (own `git show | python` sweep over the 15 canonical files, no file writes): every file is snapshot_schema "zr_section_snapshot/v1"; content_digest_sha256 == sha256(verbatim_excerpt) for all 15; extraction_status "extracted_draft" and source.raw_html_verified false on all 15; snapshot_id == filename stem; 15 distinct ids. Every "Verified" token is either `raw_html_verified: false` or the negated ADR-007 line ("Nothing in this record is a Verified zoning determination…") — nothing is affirmatively Verified. Canonical vs bundle sha256 MATCH for all 15, and equal the producer-reported digests (5a72fb9f… etc.). Tables carried in a structured `table`/`tables` field with a `[table - see structured …]` placeholder in the excerpt, matching the zr-23-432 template; 24-34 carries a `footnotes` field.

2. Production loader: `SnapshotStore().load()` (over all 215) raised no duplicate-id error; `.get()` + `load_snapshot_file` (which itself enforces the digest) loaded and digest-validated all 15 from the packaged bundle dir — 15/15.

3. Fidelity vs the official site (I fetched official HTML for all 15 sections and the print/PDF for 22-13, 24-111, 24-04, 24-56; read PDFs from the saved binaries): section number, official title, node id and Last Amended match the live page for every section; all 15 are Last Amended 12/5/2024 (datetime 2024-12-05T12:00:00Z, PDF banner "LAST AMENDED 12/5/2024"). Titles match verbatim including the long ones (24-162) and the wording the packet only paraphrased. Block-by-block text comparison is verbatim for every section I inspected, defined terms as `#term#`. Tables: 24-11 (all 3 tables, every row), 24-111, 24-162 (COLUMN A/B), 24-34 (+footnote), 24-522 all match cell-for-cell.

   LIST LETTERS — the M3-T008 trap, re-checked against the PRINT on every `<ol>` list: 22-13 print shows one continuous (a)(b)(c)(d)(e) (HTML markdown renders 1–5; the capture correctly uses the print letters); 24-111 print shows one continuous (a)(b)(c) with the 8-row table (R3=0.50 … R9=7.52) — the capture's relabelling is correct and the M3-T008 F1 pattern is handled; 24-04 print shows nested (a)/(b) → (1)/(2) → (i)/(ii) exactly as captured (the HTML markdown's 1/a/i was a rendering artifact, not the source); 24-56 print shows (a)(b)(c)(d) with the sub-headings, matching. 24-162/24-33/24-35 use literal parenthesized `<p>` labels, verbatim in both HTML and capture; 24-33's internal cross-reference "paragraph (b)(2)(ii)" confirms its (a)(b)/(1-5)/(i-iii) hierarchy is the source's own.

   PARENT-ONLY (22-13, 24-11, 24-52): confirmed each holds the parent's own text only. 22-13 print ends at (e) and the "22-131" child header begins immediately after (excerpt omits it); 24-11 HTML body stops after the parent + tables (children 24-111/112/113 not in body); 24-52 HTML body stops after the one parent paragraph (24-521/24-522 not in body).

4. Producer's disclosed quirks — each is the official page's own text and handled honestly: (a) 24-11 table-3 header lowercase "#interior Lot#" — WebFetch independently rendered "interior Lot" lowercase in table 3 only (tables 1–2 "Interior Lot"); kept verbatim and noted in header_structure. (b) 24-522 "without a letter suffix,if" no space after the comma — WebFetch independently confirmed no space; kept verbatim. (c) 24-522 illustrative SKY EXPOSURE PLANE diagram omitted, its caption kept — WebFetch confirmed an image follows the table with caption "SKY EXPOSURE PLANE R6, R7, R8, R9, R10, R11, R12 Districts", kept as the final excerpt block.

5. Scope: `git show --name-status ccf8e24be` = exactly 31 files — 15 canonical `docs/research/zr-snapshots/v1/zr-*.snapshot.json` (A), their 15 byte-identical `services/api/app/_zr_snapshots/v1/` copies (A), and `project-control/reports/M3-T009-producer-report.md` (M). No forbidden path touched (app/rules, app/scenario, app/drawings, services/api/tests, sync_zr_snapshots.py, apps/, packages/, reference-cases, zoning-rule-review, zoning-law-library, evidence-records, docs/design all clean). Every source.request_url and cross_check.request_url is on zoningresolution.planning.nyc.gov; both channels carry a 64-char sha256; http_status 200/200 on all 15. 22-13 children 22-131–22-135 exist on the site (the 22-131 header renders right after the parent list in the PDF; the HTML links all five) — listed for a later capture, no file written, nothing invented (S4).

6. Required checks (lanes venv /root/project/lanes-runtime/venv, PYTHONDONTWRITEBYTECODE=1, direct exit codes, worktree content proven byte-identical to the pin):
   - `python services/api/scripts/sync_zr_snapshots.py --check` → "OK: … byte-identical (215 file(s))." EXIT 0.
   - from services/api, PYTHONPATH set: `python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/drawings/report/test_report_law_links.py` → 28 passed. EXIT 0. (law-links green ⇒ no new section is cited by the benchmark fixture; no href changed — S3.)

=== FINDINGS (advisory only) ===

A1 — ADVISORY / limitation. For 5 of 15 (24-162=17642, 24-33=17652, 24-34=17653, 24-35=17654, 24-391=17663) the HTML fetch did not surface the `data-content-nid`, so I confirmed title/date/text but not the node glyph directly. The other 10 node ids I confirmed directly (HTML surfaced, or the `/print/pdf/node/<id>` render returned the right section: 18150, 17632, 17633, 17623, 17641, 17645, 17656, 17672, 17670, 17678). The 5 unconfirmed ids are internally consistent and each URL returned the expected section; residual risk only, not a defect.

A2 — ADVISORY (non-issue, noted for transparency). In the 22-13 print the special-permit glyph "○" renders as a blank gap in the PDF text layer; the capture correctly stored "○" from the HTML (which carries the real character). This is the right choice, consistent with the disclosed pdftotext artifacts.

A3 — ADVISORY. Directive-compliance for D-094 R102 (documents/data-only library lane, no file shared with the report lane) and R104 (research for remaining options' rules) is consistent with this documents-only capture — no rule, no reading for a lot, no computed figure — but the binding R102/R104 ↔ evidence pass belongs to the separate directive-compliance-verifier (producer ≠ verifier); I did not record that verdict.

=== WHAT I COULD NOT CHECK ===
- Could not create a `git archive` copy (role blocks shell file-writes); mitigated by proving byte-identity of all 34 task files pinned-vs-clean-HEAD and running the suites there.
- Did not re-read the per-section node glyph for the 5 sections in A1.
- Second-agent raw-HTML re-read is out of scope; raw_html_verified stays false / extraction_status extracted_draft on all 15 (correct for this task type).

Bottom line: integrity, loader, bundle byte-identity, scope, provenance discipline (nothing Verified; both channels pinned; official host; parent-only correct), both required checks, the three disclosed quirks, and the text/table/list-letter fidelity of all fifteen captures are sound. The repeated M3-T008 list-label trap is handled correctly (print-letter labels verified on 22-13, 24-04, 24-111, 24-56). Recommend PASS.

END-OF-REPORT
