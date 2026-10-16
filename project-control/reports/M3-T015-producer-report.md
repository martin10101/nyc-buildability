# M3-T015 producer report (official-source-researcher)

Task: capture the owed Zoning Resolution sections the open readings rest on that are NOT yet in
`docs/research/zr-snapshots/v1/` — the BSA community-facility special-permit categories
73-11/73-13/73-18 that ZR 24-111(a) carves out of the residential-FAR cap, the Article VII Chapter 7
"zoning lots divided by district boundaries" family, plus ZR 76-131 and ZR 35-36; attempt the
documented browser-UA print/PDF fallback for ZR 23-154 (UAP); then reconcile the law library's
capture-state flags. Documents only (D-094 R102, R258). Not professionally reviewed (ADR-007).

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a276930ac573c7def`
Contract base (reset HEAD): `b7f473690580794265c73a6323908f2ad062cf15`.
Capture run: live against `zoningresolution.planning.nyc.gov`, 2026-10-15, paced one request at a time,
browser UA (`Mozilla/5.0 … Chrome/120.0`). Every number, title, node id and Last-Amended date is taken
from the page read this pass (the H12/H13 planning returns were a cross-check, not a substitute).

## 1. Sections captured (19 definite; all prose, NO table payload)

Each is one JSON in the `zr_section_snapshot/v1` shape (template `zr-73-432`; headings modelled on the
accepted `zr-35-00`). Canonical under `docs/research/zr-snapshots/v1/`, byte-identical bundled copy
under `services/api/app/_zr_snapshots/v1/` produced by RUNNING `sync_zr_snapshots.py` (never
hand-edited). HTML `raw_html_sha256` + `response_bytes` pinned; the section's own print/PDF
(`entityprint/pdf/node/<id>` → `print/pdf/node/<id>`) is the text-check cross-check only (PDF bytes
regenerated per request, NOT pinned — DB-167). `content_digest_sha256 == sha256(verbatim_excerpt)`.
`extraction_status=extracted_draft`, `raw_html_verified=false`, ADR-007 label on every file.

| section | node | Last Amended | html bytes | content_digest_sha256 | cross-check | pdf obs bytes |
|---|---|---|---|---|---|---|
| 73-11 | 18804 | 6/6/2024 | 106250 | 9cfacedc59b980472ff5b499b63f47982e2f61cd4d728393ed96eb715f9ab9b8 | no_own_body | 52184 |
| 73-13 | 18805 | 6/6/2024 | 106240 | ddbcbcc4d7b266525e23564f4908543c15fee912ccab2b93cd7b37c047eb6b66 | no_own_body | 57088 |
| 73-18 | 22592 | 6/6/2024 | 106304 | e04b542ac7139899392fa1b4da022e789a9dfda49706db280fd85b36069b045c | no_own_body | 57750 |
| 77-00 | 18889 | 8/14/1987 | 76107 | bd37979c47d186ad1eb520b3ba81617db4f3880dc875e3daea8ea9c37ac4b3ba | no_own_body | 50005 |
| 77-01 | 18890 | 12/15/1961 | 76694 | c9bd29ec2f8571263c3ceec7cc9c4f895a8cde55d1121e87ffb41f1525a95824 | match | 45909 |
| 77-10 | 18893 | 12/15/1961 | 76102 | 44c84bf87309671f1664006d3cbb9da44d064b9f136066816c24e901d7283b4b | no_own_body | 52153 |
| 77-11 | 18894 | 6/29/1989 | 78379 | 3a1592a4b76fb0bc8b9c4a3630ce2c3359498e1a1915d65eb570036b05590eef | match | 48844 |
| 77-12 | 18895 | 6/25/1964 | 77437 | eb1cb98d2dfda866820593f52d2986e266d682ed77b2549b6dc7dee9855a912c | match | 49209 |
| 77-20 | 18896 | 12/15/1961 | 76104 | b23d088f421937370f34990769ed02b34886f663b22d569a3e3abd5e1033708b | no_own_body | 69938 |
| 77-21 | 18897 | 9/27/1962 | 77252 | 03d85cae11ada62268b47808c685c98840ac4013a084d9352642ed6906f6e4e3 | match | 50755 |
| 77-211 | 18898 | 12/5/1990 | 78373 | 366b1aa439a326640cf50db3e98706e9210e49dab2644876d73570d4ba263d02 | match | 47863 |
| 77-22 | 18899 | 12/5/2024 | 79263 | 90af26a3b4e90f308d35973fb7ed90012722c763a7409ce1a97b8f712ad82c14 | match | 47812 |
| 77-24 | 18901 | 12/5/2024 | 80308 | 6af1dcd7056fd1b755c1550352983368abaebe210caa3b1e78420c2a503b058a | match | 49425 |
| 77-25 | 18902 | 12/5/2024 | 77481 | 289121d10ce2d1b59e2f045116f6e784f3bad4081a7dae5fa3d5c14ebb1d2702 | match | 47816 |
| 77-26 | 18903 | 2/2/2011 | 76599 | add36a023dabeec899110244a7ce3b1cf75e49eff6b69d210ade2a140dcbe7f2 | match | 44007 |
| 77-27 | 18904 | 2/2/2011 | 76466 | 58e2ab36ddc1937c3f29f7ff9813838d0877f1c0c80647f720e49b1619b5cc89 | match | 44063 |
| 77-28 | 18905 | 12/5/2024 | 79280 | b04851fdf0a99e34ca986eafb7f25a772c72f237a11e47a167cf0e8d03a1190d | match | 50351 |
| 76-131 | 19083 | 12/15/1961 | 73705 | 79984de0308d64fa90b76091460346c798b81ebb32c1313f40d7b9696d42efdc | match | 46442 |
| 35-36 | 18274 | 12/5/2024 | 84591 | ff9d0e7e2b331c90bdd7fd5e21048803e75ce2eaef0b5c6dc11707f7a6b5b14e | no_own_body | 50590 |

Titles taken from each page's `<h3>`: 73-11 "Agriculture and Open Uses"; 73-13 "Community Facilities";
73-18 "Recreation, Entertainment and Assembly Spaces"; 77-00 "GENERAL PROVISIONS"; 77-01 "Applicability
of This Chapter"; 77-10 "USE REGULATIONS"; 77-11 "Conditions for Application of Use Regulations to
Entire Zoning Lot"; 77-12 "Application of Use Regulations Under All Other Conditions"; 77-20 "BULK
REGULATIONS"; 77-21 "General Provisions"; 77-211 "Conditions for application of bulk regulations to
entire zoning lot"; 77-22 "Floor Area Ratio"; 77-24 "Lot Coverage"; 77-25 "Density Requirements"; 77-26
"Minimum Lot Area and Lot Width Requirements for Residences"; 77-27 "Yard Regulations"; 77-28 "Height
and Setback Regulations"; 76-131 "Boundary line parallel to the short dimension of block"; 35-36
"Special Floor Area Ratio and Related Bulk Provisions for Certain Areas".

Dates read live DIFFER from the chapter-level cross-check in H12 ("Chapter 7 last amended 3/22/2016"):
each 77-xx page carries its OWN Last Amended (77-00 8/14/1987, 77-01/77-10/77-20 12/15/1961, 77-11
6/29/1989, 77-12 6/25/1964, 77-21 9/27/1962, 77-211 12/5/1990, 77-22/77-24/77-25/77-28 12/5/2024, 77-26/
77-27 2/2/2011) — taken from the page, not the chapter banner, per R3. 73-11/13/18 = 6/6/2024, Chapter-7
cross-check confirmed only where the page agreed.

### Heading/container sections (empty own body — `result=no_own_body`)
73-11, 73-13, 73-18, 77-00, 77-10, 77-20, 35-36 carry NO operative body text of their own (page
`div.sec-body` empty). The excerpt is the displayed `<number> <title>` only (modelled on accepted
`zr-35-00`). Each print/PDF renders the heading then its subsections; the subsections are
adjacent-not-in-batch (§5 below), not captured here. Verified by reading each PDF: 73-11 prints
73-111/73-112; 73-13 prints 73-131..73-136; 73-18 prints 73-181..73-185; 77-00 prints 77-01/77-02/
77-03; 77-10 prints 77-11/77-12; 77-20 prints 77-21..77-29; 35-36 prints 35-361/35-362.

### Extractor discipline
The verbatim excerpt was extracted programmatically from the `sec-body field--name-body` HTML: defined
terms `<strong><em>…</em></strong>` → `#term#`; one block per `<p>` and per list item in page order;
first-level ordered-list letter labels `(a)/(b)/…` taken as the section's own print renders them (only
77-22 has a true `<ol>`; its two items print (a)/(b), confirmed against node 18899's PDF); pseudo-li
paragraphs (77-211, 76-131) keep their literal `(a)/(b)/(c)` label; inline section cross-links reduced
to the printed section number; whitespace/nbsp collapsed to one space, each block trimmed; figures
omitted. BEFORE use on new sections the extractor was proven to reproduce the committed `zr-35-31`
verbatim_excerpt BYTE-FOR-BYTE (and the correct node 18266/number/title/date). Every prose section's
excerpt body words were then compared word-for-word (hyphen/line-wrap tolerant) against its own
print/PDF (`pdftotext -layout`): all `match`.

### table_digest discipline (M3-T013 / DB-276)
Every page read this pass is PROSE — no `<table>` in any `sec-body`. So NO capture carries a `table`/
`tables` payload and NONE carries `table_digest_sha256` (a stray digest would fail
`snapshots._verify_table_digest`). The table-bearing count stays 37;
`tests/rules/test_zr_snapshot_table_digest.py` is green.

## 2. ZR 23-154 (Universal Affordability Preference) — CONDITIONAL, NOT captured (dated access-blocked note)

23-154 is NOT load-bearing for the benchmark lot (per the library it is cited only for the UAP Offsite
Option floor-area rate; the substantive UAP rules live in Article II Chapter 7 / 27-111). Attempts on
2026-10-15 (browser UA, paced):
- `GET https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-154` → **HTTP 403** (a 403
  error page of 57430 bytes, not the section) — re-confirms H6/H12's 403.
- To attempt the documented `entityprint/pdf/node/<id>` fallback I need the node id. The section HTML is
  403 (carries no node), so I tried to harvest it legitimately: `GET /article-ii/chapter-3` (the chapter
  index) → **HTTP 200**, but it lists NO 23-15x section (its section links jump 23-12 → 23-20); and
  `GET /article-ii/chapter-3/23-15` (the parent) → **HTTP 404 "Page not found"**.
- No node id for 23-154 exists in the section HTML, the chapter index, any captured snapshot, or the
  library. I did NOT invent a node (S5/R3/CLAUDE.md 3), so the entityprint/pdf fallback could not be
  exercised. Per S4/S10: NO `zr-23-154` file is written (neither tree), the library's 23-154 entry
  stays NOT CAPTURED, and the UAP text/title/number/node/date is never invented or paraphrased. The run
  stopped after these paced attempts (no hammering).

## 3. Runtime bundle + library capture-state reconciliation (documents only)

Bundle: ran `python services/api/scripts/sync_zr_snapshots.py` (script RUN, never edited; it globs the
folder). 19 new byte-identical copies written under `services/api/app/_zr_snapshots/v1/`; `--check`
passes (274 files).

`docs/zoning-law-library/benchmark-r6b-sections.json`:
- counts: `captured` 70 → 71, `not_captured` 3 → 2 (`sections_total` 73 unchanged).
- 77-00 section entry → `state: captured`, `snapshot_id: zr-77-00`, content_digest bd37979c…, `coverage_status`
  not_evaluated (title-only heading, no rule computes it), `last_amended` 1987-08-14; notes list the
  captured Chapter-7 family subset and keep the "split lot" meaning OPEN (owner N1).
- 24-111 `cross_references_out`: 73-11/73-13/73-18 → `captured: true` with their `snapshot_id`s (reason
  updated; still "not followed" — project-specific carve-out, the R6B CF-FAR effect stays an OPEN reading).
- 35-30 and 35-31 `cross_references_out` for 35-36 → `captured: true` + `snapshot_id: zr-35-36`
  (NECESSARY capture-state reconciliation: zr-35-36 now exists, so leaving `captured:false` would be a
  stale flag that fails the capture-claim invariant; 35-361/35-362 children stay uncaptured).
- 23-154 and shared-housing section entries LEFT NOT CAPTURED.

Markdown capture-state flags flipped to reflect the folder (capture-state ONLY — no reading, value,
interpretation, result, or label-vocabulary change; option 8's A/B/C meaning and "not sure" readings and
24-111's OPEN R6B CF-FAR question are untouched):
- `coverage.md`: "77-00 (**NOT CAPTURED**)" → "(**captured, M3-T015**)".
- `cross-reference-closure.md`: split-lot family "77-00 NOT CAPTURED" → "captured, M3-T015"; and removed
  77-00 from the "NOT CAPTURED, in scope" list (23-154 + shared-housing remain).
- `options-sections.md`: "77-00 [NC][nH]" → "[C][nH]"; "77-00 NOT CAPTURED under reading (b)" →
  "captured, M3-T015"; the option-8 second-pass list "77-01/…/77-28, all NOT CAPTURED" → "all CAPTURED
  M3-T015".
- `options/README.md`: option-08 row "77-xx and the distance/court sections NOT CAPTURED" → "the
  distance/court sections NOT CAPTURED (the 77-xx split-lot family is captured, M3-T015)".
- `options/option-08-split-lot.md`: the Reading-B table capture column for 77-01/77-11/77-12/77-21/
  77-211/77-22/77-24/77-25/77-26/77-27/77-28 → their `zr-*.snapshot.json` filenames (mirroring the 36-64
  row); the "(none captured; bodies read live)" note → "(captured M3-T015; bodies also read live)". The
  HANDLED column stays NOT HANDLED; the 23-371/23-372/23-35 court rows stay NOT CAPTURED; the "is the
  overlay edge a district boundary — not sure" prose is untouched.
- `options/option-11-combinations.md`: "only 23-154, 77-00 and shared-housing remain not captured" →
  "only 23-154 and shared-housing"; added the 77-00 family as now captured (M3-T015). The option-8 row
  "a district-boundary split (77-00) is NOT SURE" reading is untouched.
- `option-02-03-affordable-and-senior-housing.md` left unchanged (its only relevant flag is 23-154,
  which stays NOT CAPTURED).
- `research-log.md` / `options/research-log.md` are historical search logs and OUTSIDE this task's
  allowed paths — left unchanged.

Capture-claim / cross-reference invariant (documented in research-log.md; no `verify_captures.py`
exists, so the logic was run directly): every `captured` section/cross-ref/term's snapshot_id+digest
matches a file; every NOT CAPTURED entry has no file; counts reconcile (sections 71 captured / 2 not,
terms 30/8). PASS at the frozen head.

## 4. Checks (lanes venv `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`)

- `python services/api/scripts/sync_zr_snapshots.py --check` → `OK … 274 file(s)`, exit 0.
- `cd services/api && python -m ruff check .` → `All checks passed!`, exit 0.
- `flock heavy-run.lock … pytest -p no:cacheprovider -q tests/rules/test_zr_snapshot_bundle.py
  tests/rules/test_zr_snapshot_table_digest.py tests/drawings/report/test_report_law_links.py` →
  `41 passed`, exit 0.
- library capture-claim / cross-reference check (documented logic, run directly) → PASS, exit 0.
- `python tools/modularity_check.py --check` → exit 0 (pre-existing warnings only; no file I touched).
- `python3 tools/research_record_check.py --check` → `PASS`, exit 0 (NB-04 code_current False is
  pre-existing and reported-not-failed; unrelated to this task).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → `LANE COVERAGE PASS: 10872 file(s)`, exit 0.

No api production code, scenario/drawings/rules code, tests, or `sync_zr_snapshots.py` were edited, so
no behaviour test / mutation proof applies (documents-only research task). No report page changed → no
report print. The review register pins no file this task edits.

## 5. Adjacent-not-in-batch (S8) — deferred, NOT silently omitted

- Children of the three 73-xx parents: 73-111/73-112 (under 73-11); 73-131/73-132/73-133/73-134/73-135/
  73-136 (under 73-13); 73-181/73-182/73-183/73-184/73-185 (under 73-18).
- Rest of Article VII Chapter 7: 77-02, 77-03, 77-23, 77-29, 77-30, 77-31, 77-32, 77-321, 77-322, 77-33,
  77-331, 77-332 (parking/tower/open-space; not reached by option 8's use+bulk reading).
- 35-36 children: 35-361, 35-362.
- Shared-housing use/standards (option 9; City-of-Yes framework pending 2027): stays NOT CAPTURED.
- 23-154 (UAP): access-blocked (§2); stays NOT CAPTURED.

## 6. Assumptions, limitations, what stays open

- Nothing here is a Verified zoning determination; no rule, no reading for any lot, no computed number,
  no eligibility determination (ADR-007 label on every file). Option 8's "split lot" meaning (owner N1)
  stays OPEN; 24-111's effect on the R6B community-facility FAR stays an OPEN reading question; the
  actual mapped C2-2 overlay line (ZoLa) remains unread; 23-154 remains access-blocked.
- `raw_html_sha256`/`response_bytes` pin THIS session's whole-page fetch; the page's non-body chrome
  carries a per-render Drupal `form_build_id`, so the whole-page digest can differ between sessions while
  the body is byte-stable — the reproducible semantic pin is `content_digest_sha256` over the excerpt.
  `raw_html_verified` stays false (not re-read by a second agent).
- Title case is reproduced as each page's `<h3>` shows it (uppercase for the X0 heading sections, mixed
  case for the leaves), matching the accepted `zr-35-00`/`zr-35-31` convention; the excerpt follows the
  template `zr-73-432` convention of a `<number> <title>` block [0].

END-OF-REPORT
