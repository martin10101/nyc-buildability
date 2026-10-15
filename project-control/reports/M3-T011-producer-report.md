# M3-T011 producer report — 20 ZR captures (options 5/6/7) + law-library capture-state corrections

Producer: official-source-researcher (an AI agent; this is not a human or professional/legal
review). Documents and data only — no rule, no reading of the text for any lot, no computed figure,
no eligibility determination, nothing labelled Verified. Research and verification (D-093) applied:
every official page was opened for THIS pass; each section number, title, node id and Last Amended
date is taken from the page read now, not from the brief, the planner or the library. No evidence
record was read or changed (a capture is retrieved evidence, not a reading).

Worktree `/root/project/nyc-buildability/.claude/worktrees/agent-a1e81af1d22c525e0`; reset to the
claim head `593f8c7ace9e807cd9ecd0790c87489e16827965` on `task/wave27-comparison-appendix` before
work; `git status --porcelain` was empty at reset.

## Method (same shape as accepted M3-T010 / M3-T009)

For each section: one direct HTTPS GET of the official HTML (Mozilla/5.0 user agent, host
`zoningresolution.planning.nyc.gov` only); node id read from `data-content-nid`; section title from
`data-section-title`; Last Amended from the page's own `<time datetime>` stamp. Then one GET of the
print/PDF render (`entityprint/pdf/node/<id>` → `print/pdf/node/<id>`). The `verbatim_excerpt` was
extracted PROGRAMMATICALLY from the raw HTML `sec-body`→`field--name-body` container (one block per
paragraph / list item, page order; `<strong><em>` defined terms → `#term#` exactly as the official
PRINT itself renders them; inline section-reference links kept as their text; `<br><br>` splits a
heading line from its paragraph; whitespace/nbsp collapsed to one space; no word changed). **List
labels were taken from the official PRINT** and confirmed item-by-item (the M3-T008 G1 F1 lesson):
top-level items (a),(b)…; the next level (1),(2)…; the next (i),(ii)…; pseudo-li paragraphs carry
their own in-text label. Every text block of every excerpt was cross-checked against BOTH the PDF
text layer (`pdftotext`/`pdftotext -layout`) and the HTML visible text (glyph/quote/dash/whitespace-
tolerant) — all 20 passed. `content_digest_sha256 = sha256(verbatim_excerpt)`; `extraction_status`
extracted_draft; `raw_html_verified` false on every file. Requests were paced a few seconds apart;
one capture run against the site; no three-in-a-row refusals occurred. HTTP summary: 20 section HTML
200 and 20 section PDF 200 (after the 74-902/903 URL correction below).

## Captures — all 20 written (each also byte-identical under services/api/app/_zr_snapshots/v1/)

Format: section | title | LA | node | HTML(status bytes sha256 ret) | PDF(status bytes sha256 ret) | excerpt len, digest.

- 22-131 | "Use Group III – general use allowances" | 12/5/2024 | node 22415 | HTML 200 276347B html_sha256 c82bcf57918ab99892cefa199dd4024fddc182f99f0ca881f80820cbff38ae1d ret 2026-10-15T10:51:22Z | PDF 200 61641B pdf_sha256 a3e50fc363a162407afb1646739f00c5a8048c8ce2135db54bfa09e16c5c70af ret 2026-10-15T10:56:06Z | 544ch digest a40bcc1a791a7c53bcbee29536a76ca2483dd98893325f7e85c941131712966a — TWO TABLES (A/B) + legend
- 22-132 | "Use Group III – uses subject to size limitations" | 6/6/2024 | node 22416 | HTML 200 53989B html_sha256 1cadbcca6aea342299e6939d565a411d76ea1341b477d4d01909c133d6f04df0 ret 2026-10-15T10:51:28Z | PDF 200 50871B pdf_sha256 9b1f9d7637bc40c9d8ccc1fba1b4511f587051ead902aaf16e6c827944fc4ad4 ret 2026-10-15T10:56:10Z | 1454ch digest 7aba522fcc1b64d0f15678c91c3427f074ca5c017168110addc270a6917b0e0c
- 22-133 | "Use Group III – uses subject to additional conditions" | 12/5/2024 | node 22417 | HTML 200 84302B html_sha256 6168aa7e337fd3f71d35f5169433b7f1f62d000c74d1d5355c481589f1ec7e80 ret 2026-10-15T10:51:40Z | PDF 200 52987B pdf_sha256 0ecd4e6b42fffeb8ab097b9112fd1c58bca0e870f0193b6cfa498fbea50dc1f9 ret 2026-10-15T10:56:14Z | 2562ch digest e7f8e059a1800ae73e626cac6acdb34f4e662e354960431fdbaa1622a4d5c126
- 22-134 | "Use Group III – uses permitted by special permit" | 12/5/2024 | node 22418 | HTML 200 82773B html_sha256 f56e39b91544c63104ef15599a2647a253d605829b9cace09462c53318da30fb ret 2026-10-15T10:51:49Z | PDF 200 51139B pdf_sha256 dfc71d6fdbf42ef7bffa580bfb39f613d7f37543702bd9ad3a3dc8cc743189b3 ret 2026-10-15T10:56:18Z | 1163ch digest 799bd389a507a2f137eb74ff9c4b54a959455d036f61848a311ce7d0fe1eb296
- 22-135 | "Use Group III – additional provisions for parking requirement category" | 12/5/2024 | node 22419 | HTML 200 82205B html_sha256 b9de15ae3e65ced2bbba586db1b428938148bd51ae72eec8b4ca77390dde0777 ret 2026-10-15T10:51:56Z | PDF 200 49130B pdf_sha256 abbf7ce52cc9fad0d3239f187b8bdcd32f53d14c2cd12a1f0dac2ffb0938eafe ret 2026-10-15T10:56:22Z | 696ch digest a91681ee4c683a7ed7bff2ef2449a99e2a4db1d030ef1211225d612b196b80e6
- 74-902 | "Certain community facility uses in R1 and R2 Districts and certain Commercial Districts" | 6/6/2024 | node 19198 | HTML 200 118396B html_sha256 8592e8c02d6428881de39f933e992645a1a4ce39d36a08c0bb944f323d6207e7 ret 2026-10-15T10:54:53Z | PDF 200 50713B pdf_sha256 6b314b5892e21db2f1f1a785bd8d8dd6e54de6af4a8a78ea325a43d0b0d90115 ret 2026-10-15T10:56:26Z | 2032ch digest 282db3586740487cb1ee9380ea596dab01bdbefb90ee67218c6fa1ff58f26af9
- 74-903 | "Certain community facility uses in R3 to R12 Districts and certain Commercial Districts" | 3/22/2016 | node 19199 | HTML 200 120651B html_sha256 abf5001dbe31b008546ee2aaf1d8ae6e2292236f7749f4948d9c0719baeb2ee4 ret 2026-10-15T10:55:02Z | PDF 200 52345B pdf_sha256 77e21250844c22fee592bc981a1302944dfde2fce7e1d5885157a4f384763bd4 ret 2026-10-15T10:56:31Z | 3261ch digest 9d36405940fc2c8634036693a674efbe82a9e5c394def1d0e5dd283ccecf4d39
- 23-63 | "Required Recreation Space in Multiple Dwelling Residences" | 12/5/2024 | node 17505 | HTML 200 113887B html_sha256 7dda6a47ff9dc7ce1d96f4b7e6e1662c3f59f762a28a6aac6d4f8b170a03df4f ret 2026-10-15T10:52:14Z | PDF 200 50315B pdf_sha256 699a69bf3a8b68fcc15ca6784475183d38978ba454375d740239404e0be68446 ret 2026-10-15T10:56:35Z | 1912ch digest 078cc8718ee4a2ef0c3eae5ab54e03b33006e2767806c17d95b74dddaecdb4bf
- 24-37 | "Special Provisions for Shallow Interior Lots" | 12/5/2024 | node 17658 | HTML 200 99202B html_sha256 513398eb83b5fdb8cd7b2a73acad1714ee117ecedf610a56020080fba9cfa2e2 ret 2026-10-15T10:52:21Z | PDF 200 47707B pdf_sha256 1d406acdd6e1ab23c9bf13c268a0949fcc739222f0dd0e6e86ce4da92c970953 ret 2026-10-15T10:56:40Z | 648ch digest 9f64b34aa4ae286f4318e2ddc497b9b667a3d150764b3158e24575d758c37202
- 24-38 | "Special Provisions for Through Lots" | 12/5/2024 | node 17659 | HTML 200 98550B html_sha256 531987bc3b2fb943c6e7664f9fa4c51d7d063600fd9d04deba3de65584e405f0 ret 2026-10-15T10:52:28Z | PDF 200 51100B pdf_sha256 62171ee61b5e34891b6f2d34e69d2c5b21d5e90fa6394a8f8c11b05fa2ed6a17 ret 2026-10-15T10:56:44Z | 257ch digest 38c222dcb7701b38f1b9a8cd45250ac861f64a287a50ab6d1c18b16ed0143f4b
- 24-39 | "Other Special Provisions for Rear Yards" | 12/5/2024 | node 17662 | HTML 200 98515B html_sha256 2633dd1e20c27ab23258c54d57e11a1c84370056f72b163df99192f4ca857385 ret 2026-10-15T10:52:38Z | PDF 200 90381B pdf_sha256 e4ae034cb1f5a8f6235f8a48197b8e916c2f3ab0111df98ee3a1815b30270229 ret 2026-10-15T10:56:48Z | 217ch digest 427cfd96ceecce9e95d7e273dfc8333c6bac4c282db9c0b5edf82ac9e9986fcb — PARENT heading (renders children 24-391/24-392/24-393)
- 24-392 | "Along short dimension of block" | 12/5/2024 | node 17664 | HTML 200 98557B html_sha256 0f8ad71a64ecb49174c446b60d2e3d39b2f48b490dfa058c563e10b37b73b99a ret 2026-10-15T10:52:48Z | PDF 200 46450B pdf_sha256 d14e123bd59656137811a1040271497b6caa79029e6f2bd12b6859f6d1bf7649 ret 2026-10-15T10:56:54Z | 243ch digest 76865e9fdf88ac26fe687e7e11289659d8a8d26044acf23cb76ce8247e280c4e (node confirmed live = 17664, per judge)
- 24-393 | "For zoning lots with multiple rear lot lines" | 12/5/2024 | node 17665 | HTML 200 101512B html_sha256 338d18dc68b62c71e2d3e97e0ecf2f6e0a88eec0e1797e5a8b6434053cde7bcd ret 2026-10-15T10:52:55Z | PDF 200 88236B pdf_sha256 a684edca9d221c797329aacc0d81100448b514b0b1b8c6516969049bd8a476ac ret 2026-10-15T10:56:59Z | 1310ch digest cc514b12ffdcc20d8846e5fee705b841014525675d8a19a2ccb6bce898f14043 — 3 DIAGRAM IMAGES (pointer-only; node confirmed live = 17665, per judge)
- 33-27 | "Special Provisions for Shallow Interior Lots" | 6/6/2024 | node 17740 | HTML 200 98095B html_sha256 dd0f650272ba7836193fa2b1d1e9ea97fc860cc0b094f6a0a0f41fde89843e2b ret 2026-10-15T10:53:03Z | PDF 200 48056B pdf_sha256 4534ff0d0e2b67449722eb7e7223f77b9ad5d349d5919feefa9e5d9b8cfc320f ret 2026-10-15T10:57:03Z | 1124ch digest f3a5144d0764b71e408f2af5e10dbb90b45a3024ddc956e05116a2bf57a201e7
- 33-28 | "Special Provisions for Through Lots" | 4/30/2008 | node 17741 | HTML 200 96799B html_sha256 d34a049bc4bd8c86909a63cd5c8b74930bd4f998b2dc9e13617ea2bc9e155fa4 ret 2026-10-15T10:53:10Z | PDF 200 51552B pdf_sha256 4c1b23ed4f9ebc7df08be042834efda278944fc6a1f45f4722f24e8fb1dd9d27 ret 2026-10-15T10:57:07Z | 242ch digest 4b65bba7179011549c960f9cd0e1d274e9f04b8d8c122a1bdee2335934922568
- 33-30 | "OTHER SPECIAL PROVISIONS FOR REAR YARDS" | 12/15/1961 | node 17749 | HTML 200 96756B html_sha256 3a3bf31327e37d1f268ad4ba83436fe65fbe58961a7e5c66a3125ee60c8872d8 ret 2026-10-15T10:53:17Z | PDF 200 78698B pdf_sha256 d7db4e490aa26e09a4cdf9f1f7d65707540084c14c870967cbfa1a31cd77db96 ret 2026-10-15T10:57:13Z | 190ch digest 9af302700d36bb8a56d90f2018147ae77eb1e2a60e01905233788a549cb71c5a — PARENT heading (title all-caps as the page shows; renders children 33-301/33-302/33-303)
- 33-302 | "Along short dimension of block" | 12/5/2024 | node 17751 | HTML 200 96830B html_sha256 a1750f2aee571faa1446ce4bc686d9e091aa9098475417ca920cb1d9b537a64f ret 2026-10-15T10:53:23Z | PDF 200 46422B pdf_sha256 ce9e3d0ab35d28e0af37fceaf62ebbc421a92c9e436c97c80efa4d3585924aa7 ret 2026-10-15T10:57:17Z | 247ch digest 72ff0cf34e188755f505b6d496fb8c04b425803f5548856f92ef82bf091f49fe
- 33-303 | "For zoning lots with multiple rear lot lines" | 4/30/2008 | node 17752 | HTML 200 99003B html_sha256 4b6a5963ba76d56a85ed3521cba8db69de869f92bb73ad74922dc2ab469e5f15 ret 2026-10-15T10:53:31Z | PDF 200 72129B pdf_sha256 e8761328c7883cb71b8cf37ea2c7d2a4f831b2be981cb7159a7877828cddca75 ret 2026-10-15T10:57:21Z | 971ch digest aa3792cc0aeda3b0846331706ef7d6fd21e9f81b86b8fa48aed656b1cb852cb2 — 2 DIAGRAM IMAGES 33-303a/33-303c (pointer-only; printed captions kept verbatim)
- 35-23 | "Residential Bulk Regulations in Other C1 or C2 Districts or in C3, C4, C5 or C6 Districts" | 12/5/2024 | node 18264 | HTML 200 85243B html_sha256 d9d00001246a59f8638c6b54b6776d57452eb5f01cfa96746be8b0f2017fb387 ret 2026-10-15T10:53:41Z | PDF 200 46330B pdf_sha256 799d2504d37fc5e9c36219dad028907e53f5ab0f9a387f380c069f54416a3c92 ret 2026-10-15T10:57:27Z | 258ch digest 083ccbc58aa9dfd039d2c41bf52e9e3a1e788d614848107033cafbff50a863e6 — single sentence → 34-112 residential equivalent
- 35-24 | "Applicability of Residential Bulk Rules to Non-residential Portions of Mixed Buildings" | 12/5/2024 | node 22817 | HTML 200 90006B html_sha256 26e8b291186623e38fa6a07d8eec25d482fd2ced3f8e102b13edc89451530fb7 ret 2026-10-15T10:53:48Z | PDF 200 55396B pdf_sha256 e80fe3bfea7983dd592be1bef4d08564e1869cd89d5fab6161f42a301b60ee28 ret 2026-10-15T10:57:31Z | 2883ch digest b172157bd03889ee2be0f7343f86340bd8667d8d6e1fb2f412e4dd62c093d75a — three-level nested list (a)/(1)/(i)

All 20 section numbers matched the packet; every node id and Last Amended date read live this pass
equals the planner's 2026-10-15 cross-check (and the judge's confirmation 24-392 = 17664, 24-393 =
17665). Titles are the official `data-section-title` read now; several are fuller/differently cased
than the planner's description (74-902/903 full titles; 33-30 is ALL-CAPS "OTHER SPECIAL PROVISIONS
FOR REAR YARDS" while 24-39 is title-case "Other Special Provisions for Rear Yards"; 35-23 full
title). Each file records the official title read now.

## S4 finding — 74-902 / 74-903 are NOT at the guessed chapter path (resolved, not invented)

The brief/planner inventory placed the CF special permits in Article VII Chapter 9. A GET of
`article-vii/chapter-9/74-902` and `.../74-903` returned **HTTP 404** (2026-10-15T~10:53Z). I did
NOT invent a path: I fetched the sections by their planner-verified node ids
(`/node/19198`, `/node/19199`, both HTTP 200) and read each page's own
`<link rel="canonical">`, which resolves to **`article-vii/chapter-4/74-902`** and
**`article-vii/chapter-4/74-903`** (chapter 4 "Special Permits by the City Planning Commission", not
chapter 9). I then fetched those canonical article/chapter/section pages (HTTP 200) and recorded them
as `request_url`. Node ids (19198/19199) and dates (6/6/2024; 3/22/2016) match the planner exactly.
No other listed node was missing or renumbered; all 20 exist under the current (City of Yes) text.

## S8 — parents/children captured, and adjacent not-in-batch nodes (for a later capture, never silently omitted)

Captured this pass: 22-131…22-135 (children of 22-13, captured M3-T009); the CF rear-yard subtree
24-37/24-38/24-39(parent)/24-392/24-393 (24-391 already captured); the commercial rear-yard subtree
33-27/33-28/33-30(parent)/33-302/33-303 (33-301 already captured); 23-63; 74-902/74-903; 35-23/35-24.
**Deferred, NOT in this batch** (listed, never silently omitted): 23-154 (HTTP 403, access-blocked,
its own task); the 25-30 non-residential/CF parking subtree 25-31…25-37 (node 17559, a dedicated
parking task); the Article VII Chapter 7 district-boundary family 77-01/77-11/77-12/77-21/77-211/
77-22/77-24/77-25/77-26/77-27/77-28 (not this lot's situation); 23-38 (node 22767) and 23-72 (node
22778, Brooklyn CD12) short-block, not the Queens benchmark; the 12-10 "residential building" term
(whether it is a distinct 12-10 defined term was NOT investigated this pass — out of this batch;
verify before capturing, report if not — its partner "side lot line" is already captured). No option
meaning is asserted by any capture.

## S7 — table / legend / diagram handling

- 22-131 carries TWO tables — III(A) "Community Facilities with Sleeping Accommodations" (13 data
  rows) and III(B) "Community Facilities without Sleeping Accommodations" (20 data rows), each keyed
  by Residence District (columns: Uses; R1–R12; PRC). Each is carried cell-by-cell in the structured
  `tables` field, replaced in the excerpt by `[table - see structured \`table\` field]` with its
  all-caps caption kept as a block before the placeholder. The section's OWN legend is quoted
  verbatim (M3-T010 F1): `● = Permitted ♦ = Permitted with limitations ○ = Special permit required
  – = Not permitted S = Size restriction P = Additional conditions`. The `header_structure`/`method`
  notes do NOT restate any glyph meaning (A2) — the meanings live only in the quoted legend. The
  use-allowance glyphs and the PRC-column codes are the canonical HTML's verbatim cell values; the
  print/PDF text layer renders the glyphs as "?" and does not expose the PRC codes, so those cells are
  HTML-canonical and the PDF cross-check is symbol-insensitive for them (disclosed). The use names,
  category rows and Uses/R1–R12 column headers were confirmed in the PDF.
- 33-303 (2 diagrams 33-303a, 33-303c) and 24-393 (3 diagrams, uncaptioned) carry embedded IMAGES.
  Each image is captured as a POINTER only (image URL + alt text in a `figures` field) and replaced
  in the excerpt by `[figure - official diagram image omitted; see \`figures\` field]` at its page
  position — never transcribed, redrawn, or read for any dimension (the way Appendix F is a pointer
  capture). The printed figure captions "(33-303a)"/"(33-303c)" that the page itself shows are kept
  as verbatim text blocks.

## Library capture-state corrections (capture-state only; no reading, number or value changed; per S10)

docs/zoning-law-library/options/option-06-07-community-facility.md:
- Table row (22-13 / 22-131…22-135): capture cell `zr-22-13.snapshot.json (parent); 22-131…22-135
  NOT CAPTURED` → `… 22-131…22-135 CAPTURED (M3-T011)`. Reason: the five children now captured.
- Reading prose "CF use permission": `(22-13 captured; 22-131…22-135 not captured)` → `(22-13
  captured; 22-131…22-135 captured (M3-T011))`. Capture-state only; the "not sure" on which UG III
  uses are as-of-right vs size-limited vs special-permit is a reading and was LEFT unchanged.
- Capture-state preamble: appended a bounded, explicitly-labelled capture-state bookkeeping sentence
  that 24-37/24-38/24-39 (named in the CF-yards reading as "subject to 24-37/38/39") are now also
  CAPTURED (M3-T011). Per the judge's correction #2, nothing was "added" for sections the file does
  not name (74-902/903, 24-392/393 are not named in this file → no row).

docs/zoning-law-library/options/option-05-shops-with-residences.md:
- Table row 32-421: `NOT CAPTURED` → `zr-32-421.snapshot.json (M3-T010)`. Reason: captured by M3-T010.
- Table row 33-26: `NOT CAPTURED` → `zr-33-26.snapshot.json (M3-T010)`. Reason: captured by M3-T010.
- Table row 33-301: `NOT CAPTURED` → `zr-33-301.snapshot.json (M3-T010)`. Reason: captured by M3-T010.
- "What is not sure" item 5: `Capture owed: 32-421, 33-26, 33-27, 33-28, 33-30, 33-301 are NOT
  CAPTURED (read live by HX1/HB). Next step: capture these before a rule cites them.` → `Capture
  state (was "capture owed"): 32-421, 33-26, 33-301 CAPTURED (M3-T010); 33-27, 33-28, 33-30 CAPTURED
  (M3-T011). (Capture-state only; no reading added here.)` Reason: all six now captured (the three
  stale M3-T010 marks + the three this pass). Scoped to exactly the sections item 5 names.

docs/zoning-law-library/options-sections.md:
- §5 note: `32-421/33-26/33-301 CAPTURED (M3-T010), 33-27/33-28/33-30 NOT CAPTURED.` → `… 33-27/
  33-28/33-30 CAPTURED (M3-T011).`
- §9 note: `22-121 / 22-122 / 23-51 / 32-121 / 54-311 CAPTURED (M3-T010); 22-131…22-135 NOT
  CAPTURED.` → `… 22-131…22-135 CAPTURED (M3-T011).`
  (Per the judge's correction #1, only the two marks this file actually carries were flipped; no row
  was added for 23-63/74-902/903/24-37…/33-302/303/35-23/24, which the file does not name.)

docs/zoning-law-library/benchmark-r6b-sections.json (only the entries it already lists — 74-902,
74-903, 23-63 — per judge A3; JSON stays valid, `json.load` OK):
- 23-63 cross-reference (inside the 23-62 entry): `"captured": false` → `true`; reason `balcony
  cross-reference; NOT CAPTURED; out of scope; not followed` → `balcony cross-reference; CAPTURED
  (M3-T011; zr-23-63.snapshot.json); out of scope; not followed`. The 23-62 entry's `notes`:
  `23-30 yard header / 23-63 NOT CAPTURED / out of scope.` → `… 23-63 CAPTURED (M3-T011) / out of
  scope.` The disposition ("out of scope; not followed") was preserved unchanged.
- 74-902 cross-reference: `"captured": false` → `true`; reason `…NOT CAPTURED; project-specific, not
  followed` → `…CAPTURED (M3-T011; zr-74-902.snapshot.json); project-specific, not followed`.
- 74-903 cross-reference: same correction → `…CAPTURED (M3-T011; zr-74-903.snapshot.json);
  project-specific, not followed`.

Residual stale mark LEFT UNCHANGED (out of S10's enumerated scope; reported for a later pass, the way
M3-T010's planner flagged option-11): option-05 line 62, the reading heading "On which storeys shops
may sit (32-421, not captured, read by HX1 live 6/6/2024)", still says "not captured" for 32-421
(captured by M3-T010). S10 scopes option-05 to lines 22/25/26 and item 5 only; this parenthetical is
inside a reading paragraph, so it was not edited (no new reading). Also observed but NOT in scope: the
index lists `24-111` "captured": false (captured by M3-T009) and section 32-10's "Use Group
use-allowances header; NOT CAPTURED" (22-13/32-131 are captured) — both are prior-task residuals, not
among this task's 20 sections and not listed in S10; left for a future capture-state pass.

## Checks (direct exit codes; lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider under flock)
- `python services/api/scripts/sync_zr_snapshots.py --check` → EXIT 0 ("255 file(s) byte-identical").
- `cd services/api && python -m ruff check .` → EXIT 0 ("All checks passed!").
- `cd services/api && flock .../heavy-run.lock python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/drawings/report/test_report_law_links.py` → EXIT 0 (28 passed).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → EXIT 0 ("LANE COVERAGE PASS: 10684 file(s)").
- index JSON load: `python3 -c json.load(benchmark-r6b-sections.json)` → EXIT 0 ("INDEX JSON VALID").

## Producer self-check (own script, all 20 new files) — ALL PASS
For every file: `content_digest_sha256 == sha256(verbatim_excerpt)`; the production loader
`app.rules.snapshots.load_snapshot_file` loads it without error; `snapshot_id == filename` stem and
unique; `extraction_status extracted_draft`; `source.raw_html_verified false`; no stray "Verified"
beyond the `raw_html_verified` field and the ADR-007 negation; the first and last non-placeholder
excerpt blocks are found in the fetched raw HTML. Independently, every text/caption block of all 20
excerpts was confirmed present in BOTH the PDF text layer and the HTML visible text
(glyph/quote/dash/whitespace-tolerant); 22-131 both tables' use-name/category/column-header/caption
cells were confirmed in the PDF (glyph + PRC-code cells HTML-canonical, disclosed). Each byte-identical
bundled copy under services/api/app/_zr_snapshots/v1/ was produced by RUNNING sync_zr_snapshots.py
(never edited).

## What I could not check / limitations
- No second-agent re-read of the raw HTML — `raw_html_verified` stays false; `extraction_status`
  extracted_draft on every file (by design).
- 22-131 table use-allowance glyph cells and PRC-column codes do not render in the print/PDF text
  layer, so those cells are HTML-canonical and the PDF cross-check is symbol-insensitive for them
  (the HTML channel is sha256-pinned). Diagram images (33-303, 24-393) are pointer captures only.
- The print/PDF is regenerated per request (banner date), so each raw_pdf_sha256 pins the exact render
  cross-checked; a re-fetch would differ in bytes though not in printed text (DB-167).
- A capture changes no result, rule, label or evidence record (D-093). No evidence record, reference
  case, rule, scenario, drawing, test or script was edited; sync_zr_snapshots.py was RUN, never edited.
