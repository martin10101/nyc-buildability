# M3-T010 producer report — 20 ZR captures (options 5, 8, 9-10) + law-library capture-state corrections

Producer: official-source-researcher (an AI agent). Documents and data only — no rule, no reading of
the text for any lot, no computed figure, no eligibility determination, nothing labelled Verified.
Research and verification (D-093) applied: every official page was opened for THIS pass; each section
number, title and Last Amended date is taken from the page read now, not from the brief, the comparer
or the library. No evidence record was read or changed. Option 8's meaning (N1) and option 10's distinct
meaning (N2) stay open owner questions; a capture chooses neither.

Worktree `/root/project/nyc-buildability/.claude/worktrees/wf_4772a445-caa-1`; reset to the claim head
`b2bb6991e7c14a022eeb1e52f47130674cd992f6` on `task/wave26-envelope-constraints` before work.

## Method (same shape as accepted M3-T009 / M3-T008)

For each section: one direct HTTPS GET of the official HTML (`curl -A Mozilla/5.0`, host
`zoningresolution.planning.nyc.gov` only), node id read from `data-content-nid`, then one GET of its
print/PDF render (`entityprint/pdf/node/<id>` → `print/pdf/node/<id>`). The `verbatim_excerpt` was
extracted PROGRAMMATICALLY from the raw HTML `sec-body`→`field--name-body` container (one block per
paragraph / list item; `<strong><em>` defined terms → `#term#`; a double `<br><br>` splits a heading
line from its paragraph; inline section-reference links kept as their text; embedded figures omitted;
whitespace/nbsp collapsed to one space; no word changed). **List labels were taken from the official
print/PDF** and verified item-by-item (the M3-T008 G1 F1 lesson): for all 18 section pages the engine's
HTML-position label sequence equalled the print's label sequence exactly. Each excerpt block was
cross-checked against the print/PDF text layer (`pdftotext -layout`, parent portion only for parent
sections); every block was found verbatim (symbol-, label-, whitespace- and hyphen-tolerant). Tables are
carried cell-by-cell in a structured `tables` field (caption, legend where a symbol key is printed,
columns, a header-structure note, rows — every cell verbatim with `#term#`) and replaced in the excerpt
by `[table - see structured \`table\` field]`. `content_digest_sha256 = sha256(verbatim_excerpt)`;
`extraction_status` extracted_draft; `raw_html_verified` false on every file. Requests were paced (a few
seconds apart); one capture run against the site. HTTP summary: 18 section HTML 200; 18 section PDF 200;
12-10 whole-page HTML 200; 12-10 whole-page PDF 504 and both per-term PDFs 403 (the documented DB-167
fallback). No refusal of a section page occurred; no three-in-a-row stop.

## Captures — all 20 written (each also byte-identical under services/api/app/_zr_snapshots/v1/)

- 23-51 "Applicability" LA 12/5/2024; HTML node 22753 HTTP 200 raw_html_sha256 5561f0b8ddfa6584acbe1e1a087c70537619be2641655fbc923a3a6de78d02c1 (ret 2026-10-15T05:58:16Z); PDF raw_pdf_sha256 61d462677f66334605d4bdda34ed4436a17d3aadd876a72280a6e0d0129787d8 (ret 06:04:38Z); excerpt 481 ch
- 22-12 "Use Group II – Residences" LA 12/5/2024; HTML node 18149 raw_html_sha256 f2da8708de4499ff73e264597927aca191461459e6d48d8c2dadc4e1ab5f7b52 (05:58:20Z); PDF raw_pdf_sha256 ac51f4253669da077c04e9e38969f074dd4b7ec2ff6b4c028d4aca088bb1a0c3 (06:04:43Z); excerpt 489 ch; PARENT (renders children 22-121, 22-122)
- 22-121 "Use Group II – general use allowances" LA 12/5/2024; HTML node 22412 raw_html_sha256 e5f87fffb8048952dce3fdf60845167d61fbe69e15d2eed7eab6bfe94b4f05c9 (05:58:28Z); PDF raw_pdf_sha256 97026fd3dd75b85282b5d3c1d7b7c3fdfe7eb27f248d87867f12a63403e76684 (06:04:49Z); excerpt 278 ch; 1 table (Use Group II residential-uses allowance matrix)
- 22-122 "Use Group II – uses subject to additional conditions" LA 12/5/2024; HTML node 22414 raw_html_sha256 6065755ffec0af4145f4faaf19882770e8455d2f5d48dd2dc8cf65964e5e5254 (05:58:32Z); PDF raw_pdf_sha256 e44646737b7ffd6f2ab4a8cf9256c7b5beba2f7985b48d946f0e9c807bb2b430 (06:04:53Z); excerpt 1412 ch
- 32-121 "Use Group II – general use allowances" LA 6/6/2024; HTML node 22450 raw_html_sha256 e628fd549b5c4652b1d08e40da0e98b58f5cd621a0792c4050c61809ef103ae0 (05:58:42Z); PDF raw_pdf_sha256 b4ed15aad1554f4f5f854e0bc3db02ded401f5359c9343ffcd55c9b5b2940983 (06:04:58Z); excerpt 279 ch; 1 table (Use Group II residential uses in C districts)
- 54-311 "Buildings containing rooming units" LA 12/5/2024; HTML node 18614 raw_html_sha256 7202d195daa1a024106ccf2e02cb39c6c77cb4b98768772708d8fbb649a55c2f (05:58:48Z); PDF raw_pdf_sha256 e61de3255e3a55bacd1fa2f73abf4bc9b257abb4a780f1d18614a2162a0f8372 (06:05:04Z); excerpt 213 ch
- 25-24 "Special Provisions for Certain Areas" LA 12/5/2024; HTML node 17546 raw_html_sha256 fa8e9ba92f177b420064727668ade10cfb10e916c096817e2032013fd32bdd6c (05:58:57Z); PDF raw_pdf_sha256 fed97ef50550828ac123f798aefa6dad2805c53cf4b1c81e287bfea7dc04837b (06:05:09Z); excerpt 42 ch; HEADING-ONLY (empty div.sec-body; see below)
- 25-241 "Special provisions for certain community districts" LA 12/5/2024; HTML node 17547 raw_html_sha256 d2898354c1efb053c20f5bf9ee3752b87ee0cd87dc57ce7104a45ada6481102f (05:59:05Z); PDF raw_pdf_sha256 6986eef322d35ad13d3e2a73a957183e4ed92275a76ac73711dbcf2cff4486e3 (06:05:13Z); excerpt 1005 ch
- 12-10 "Transit Zone, Inner" (defined term, /node/22739) LA 12/5/2024; whole-page HTML node 18523 HTTP 200 raw_html_sha256 ab5af610c23579059bfa2d5c99d9ba4f0ef171afece7e637f2a6920fb8262572 (06:00:12Z); PDF whole-page 504 + per-term 403 → documented fallback, cite by words (06:07:07Z); excerpt 978 ch
- 23-12 "Lot Area and Lot Width Regulations in R6 through R12 Districts" LA 12/5/2024; HTML node 22747 raw_html_sha256 62e146da2b4c054a7396b14b100989edfa787ef34849de3a21a02736c818a90a (05:59:09Z); PDF raw_pdf_sha256 77405c486cbb1a814f0525ef5b717fde500773673ea4318adec2422be10a061b (06:05:18Z); excerpt 271 ch; 1 table (min lot area/width 2,375/25 & 1,700/18)
- 23-371 "Standard minimum distance between buildings" LA 12/5/2024; HTML node 18102 raw_html_sha256 fcd002e2122d8ed245e7dd061865799af5c15630a0124cab9503b1222cefeb37 (05:59:18Z); PDF raw_pdf_sha256 6dc8700078e3d215637cd19cd0510799c12b2ad1d02530314337c3fc82883d7a (06:05:23Z); excerpt 5225 ch; 2 tables (distance; small-lot aggregated coverage)
- 23-372 "Distance between legally required windows and lot lines" LA 12/5/2024; HTML node 18116 raw_html_sha256 14c5520fb0238236c8bf1b1af00dd6748bbcc96f0d985952d1aa86ae2b8aca0a (05:59:26Z); PDF raw_pdf_sha256 7c42252fc0ae5f9bfbfc23ed837ea957d975d6c5f5b59395ada56e9fef80901e (06:05:28Z); excerpt 2546 ch
- 23-35 "Court Regulations" LA 12/5/2024; HTML node 18107 raw_html_sha256 287ef15388aa3395a7f73fccddb9f37cbbe23f28e5f46365a9951236c050d164 (05:59:34Z); PDF raw_pdf_sha256 d64cd63c67668f6bc33c52461f49f684d7555a2603aa7a984d028b7fdab0cee6 (06:05:33Z); excerpt 659 ch; PARENT (renders children 23-351, 23-352, 23-353)
- 23-351 "Permitted obstructions in courts" LA 12/5/2024; HTML node 18120 raw_html_sha256 743352dfa17ead6f07b939037c5a6eabfdf49de765915d96a73e5e6d39b316d7 (05:59:43Z); PDF raw_pdf_sha256 c8397cd325cb619163f44786f57e37b2051d528de0e58bf75e05c0afd31f471e (06:05:38Z); excerpt 1467 ch
- 23-352 "Inner court regulations" LA 12/5/2024; HTML node 18114 raw_html_sha256 f24a8be48ae1c0aff41b3f05f69f50b0ce817c3985b2e81542e6b7810f69514c (05:59:51Z); PDF raw_pdf_sha256 9e74acaacc3e984cb9c44edac4b020cea204901ab3527639c88bec555d9a3050 (06:05:43Z); excerpt 1514 ch
- 23-353 "Outer court regulations" LA 12/5/2024; HTML node 18109 raw_html_sha256 3428a563e6161fb35da221d1a2411aa4b5e3d0a3a5e005d3601eb61c28603ca9 (05:59:59Z); PDF raw_pdf_sha256 14882ba619e015a1aeb6857bb84dc9ed31c42b8ab3b07e38d06ba59fc43fbd57 (06:05:48Z); excerpt 1187 ch
- 32-421 "Limitation on floors occupied by commercial uses" LA 6/6/2024; HTML node 17844 raw_html_sha256 abfc7bdf285452afef7b9a8cdd4cedf20e0f702559baecb390ebd5726ce62a6f (06:00:04Z); PDF raw_pdf_sha256 8e9344fbcfafe1281f7896a1d1abb9d39e5ad3a0cf2e175ba0f29f4c5633c510 (06:05:53Z); excerpt 1379 ch
- 33-26 "Minimum Required Rear Yards" LA 6/6/2024; HTML node 17738 raw_html_sha256 d54e9b9cdcd23db2192c75de3bb528da62069c5c2e710f256f2777c1aa073550 (06:00:08Z); PDF raw_pdf_sha256 afd9fcebae1db6c8826c6d6ad6624178dec729c03a12178458fb93f1e67c6028 (06:05:58Z); excerpt 671 ch; PARENT (renders children 33-261, 33-262)
- 33-301 "Within one hundred feet of corners" LA 12/15/1961; HTML node 17750 raw_html_sha256 5bca5b2f5beb0f40f625b84258b55f9d174f6d265184601cb0aa6671de82a889 (06:07:35Z write-time of saved HTML; page fetched at session start); PDF raw_pdf_sha256 5a008e6338d44695b38ae2c8117b757aecc841fc70b6ce46e9565ef9cd3f98ce (06:06:03Z); excerpt 205 ch
- 12-10 "Select commercial overlay" (defined term, /node/22544) LA 6/6/2024; whole-page HTML node 18523 HTTP 200 raw_html_sha256 ab5af610c23579059bfa2d5c99d9ba4f0ef171afece7e637f2a6920fb8262572 (06:00:12Z); PDF whole-page 504 + per-term 403 → documented fallback, cite by words (06:07:07Z); excerpt 152 ch

All 20 section numbers matched the packet. All titles are the official page titles read this pass;
several differ in wording from the packet's/library's paraphrase (e.g. 23-51 official title is
"Applicability", not "rooming units outside the density rules"; 25-24 is "Special Provisions for
Certain Areas", not "parking general rule"; 23-371 is "Standard minimum distance between buildings").
Each file records the official title read now.

## Sections not captured / parent & heading findings (S4, S8)

- **No listed node was missing or renumbered.** All 20 exist under the current (12/5/2024 City of Yes /
  6/6/2024) text. All 20 files were written.
- **25-24 is a HEADING-ONLY parent.** Its HTML `div.sec-body` is EMPTY — it has no operative body of its
  own; the only child its print/PDF (node 17546) renders is 25-241 (captured in this batch). Per the
  accepted zr-23-44 / zr-35-64 precedent for heading sections, its excerpt is the displayed section
  number and title ("25-24 Special Provisions for Certain Areas"); the loader fails closed on an empty
  excerpt, and no text was invented. Disclosed in the file's cross_check.result ("no_own_body"),
  composition note and notes.
- **"Select commercial overlay" DOES exist as a 12-10 defined term** (RISK 6 resolved): the term is
  "Select commercial overlay" (only "Select" capitalised — my first lowercase/title-case searches
  missed it); /node/22544, LA 6/6/2024; it lists C1-1..C1-4 and C2-1..C2-4 Districts (so C2-2 is a select
  commercial overlay). Captured. "Transit Zone, Inner" exists as the operative inverted-title term
  (/node/22739, LA 12/5/2024; "Inner Transit Zone" is a "see" cross-reference). Captured.
- **Adjacent child/parent nodes found but NOT in this batch** (for a later capture, never silently
  omitted): 22-12 → children 22-131…22-135 (NOT captured). 33-26 → children 33-261 "Beyond one hundred
  feet of a street line", 33-262 "Minimum rear yards for C7 Districts" (NOT captured). 33-301, 32-421,
  23-372, 23-12, 23-351/352/353, 23-371, 54-311, 25-241, 22-121, 22-122, 32-121, 23-51 are leaf
  sections (no children). 23-35's children (23-351/352/353) are all captured here.

## Library capture-state corrections (capture-state only; no reading, number or value changed)

docs/zoning-law-library/options/option-02-03-affordable-and-senior-housing.md:
- Rows 25,26 (12-10 senior sub-terms): `NOT CAPTURED` → `zr-12-10-affordable-independent-residence-for-seniors.snapshot.json` / `zr-12-10-long-term-care-facility.snapshot.json`; "(per HA)" date → 12/5/2024; term name drift corrected to the singular official term "affordable independent residence for seniors" (the captured term is singular). Reason: both now captured (M3-T008).
- Rows 33,34,35,36,37 (27-111/131/133/14/151): `NOT CAPTURED` → `zr-27-111/131/133/14/151.snapshot.json`; stale "(per HA)"/"not read" dates → 12/5/2024. Reason: all captured (M3-T008).
- Prose: "Article II, Chapter 7 (not captured, not handled)" → "(now captured by M3-T008, not handled)"; "§27-111 (not captured)" → "(captured)"; AIRS term "residences"→"residence"; "§12-10 general definitions (not captured)" → "(captured)"; "(§27-14, per HA; not captured)" → "(§27-14, captured)"; item 3 "Article II Chapter 7 ... and Appendix F are NOT CAPTURED and NOT HANDLED. Next step: capture ..." → "are now CAPTURED (M3-T008; ...zr-appendix-f) but NOT HANDLED. Next step: a rule may now cite ...". 23-154 kept NOT CAPTURED (not in folder).

docs/zoning-law-library/options/option-06-07-community-facility.md:
- Line 17-18: "No zr-24-* snapshot exists, so every Article II Chapter 4 section is NOT CAPTURED." → "Every Article II Chapter 4 section listed below is now CAPTURED (M3-T009; ...)". Reason: every zr-24-* now in the folder.
- 14 table rows (24-11/111/161/162/163/04/52/522/56/33/34/35/36/391): capture column `NOT CAPTURED` → the row's `zr-24-XX.snapshot.json`; 24-163 "not read" date → 12/5/2024.
- Row 22 (22-13 / 22-131…22-135): → "zr-22-13.snapshot.json (parent); 22-131…22-135 NOT CAPTURED" (parent captured M3-T009; children not).
- Prose lines 61, 89-90, 96, 129, 138-139: CF Use Group III "22-13 captured; 22-131…22-135 not captured"; "These 24-xx sections are NOT CAPTURED" → "now CAPTURED (M3-T009)"; "All NOT CAPTURED" → "All now CAPTURED (M3-T009)"; "(24-11, not captured)" → "(24-11, captured)"; item 2 "...NOT CAPTURED. Next step: capture..." → "...now CAPTURED (M3-T009). Next step: a rule may now cite them (24-161 directly supplies the R6B combination ceiling, 2.00); not yet handled.".

docs/zoning-law-library/options-sections.md:
- Line 155 (the named correction): "66-11 transit-zone definitions [C]" → "66-11 'mass transit station' [C]" (66-11 defines "mass transit station", not the transit zone; the 12-10 terms are the transit-zone definition).
- New-captures' states swept to [C]/CAPTURED where named: 27-xx + Appendix F + senior sub-terms (M3-T008); every zr-24-* incl. 24-11/24-111/24-163 and the CF height/yard sections (M3-T009); 32-421/33-26/33-301 (opt 5); 23-371/23-372/23-35/23-351/23-352/23-353 court group (opt 8); 22-12/22-121/22-122/23-51/32-121/54-311 (opt 9); "Transit Zone, Inner"/25-24/25-241 (opt 10). Still-NOT-CAPTURED left as-is and verified absent from the folder: 23-154, 77-00/77-xx, 33-27/33-28/33-30, 22-131…22-135, CF parking 25-30+.

docs/zoning-law-library/benchmark-r6b-sections.json:
- 32-131 entry (Use Group III, community facilities): scope_status "followed: option 5/11 (C2-2 retail use permission)" → "followed: option 6/7 (Use Group III = community-facility use permission; the C2-2 retail permission for option 5/11 is 32-161 / Use Group VI)"; its 32-10 cross-ref reason re-pointed to option-6/7. 32-161 (Use Group VI) keeps the C2-2 retail-permission pointer (it is the correct retail section). Reason: the comparer part-4 finding. The index references none of the 20 new sections (first-pass index; verified by grep), so no new index entries were added. JSON stays valid (json.load OK).

## Checks (direct exit codes; lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider under flock)
- `python services/api/scripts/sync_zr_snapshots.py --check` → EXIT 0 ("235 file(s) byte-identical").
- `cd services/api && python -m ruff check .` → EXIT 0 ("All checks passed!").
- `cd services/api && flock .../heavy-run.lock python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/drawings/report/test_report_law_links.py` → EXIT 0 (28 passed).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → EXIT 0 ("10544 file(s), each owned by exactly one lane").
- `python3 -c json.load(benchmark-r6b-sections.json)` → EXIT 0 ("INDEX JSON VALID").

## Producer self-check (own script, all 20 new files) — ALL PASS
For every file: `content_digest_sha256 == sha256(verbatim_excerpt)`; the production loader
`app.rules.snapshots.load_snapshot_file` loads it without error; snapshot_id == filename stem; ids
unique; the excerpt's first and last blocks are found in the fetched raw HTML (tag-stripped visible
text); every table cell (non-symbol) is found in the raw HTML. For the 18 section pages: the engine's
list-label sequence equalled the print/PDF label sequence exactly, and every text block was found in the
print/PDF parent portion. Library capture-state marks were swept against the folder listing.

## What I could not check / limitations
- No second-agent re-read of the raw HTML — `raw_html_verified` stays false; `extraction_status`
  extracted_draft on every file.
- The two 12-10 defined terms have NO print/PDF cross-check (whole-page PDF 504; per-term PDF 403, each
  attempted once): their list-item labels are markup-position representations (ZR (a)/(1)/(i) scheme),
  not confirmed glyphs — cite items by words (DB-167 F1). Item text is verbatim from the sha256-pinned
  canonical HTML.
- Use-allowance symbol glyphs (●○♦ and the en-dash –) in the 22-121 / 32-121 matrices are the canonical
  HTML's; the pdftotext text layer renders them as "?", so each symbol cell is HTML-canonical and the PDF
  cross-check is symbol-insensitive (the district headers, use names and captions were confirmed in the
  PDF). The print/PDF is regenerated per request (banner date), so each raw_pdf_sha256 pins the exact
  render cross-checked; a re-fetch would differ in bytes though not in printed text.
- A capture changes no result, rule, label or evidence record (D-093). No evidence record, rule,
  scenario, drawing, test or script was edited; `sync_zr_snapshots.py` was RUN, never edited. Option 8's
  and option 10's meanings remain open owner questions; this capture decides neither.
