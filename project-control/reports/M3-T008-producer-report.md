# M3-T008 producer report — affordable/senior-housing ZR captures (Article II Chapter 7, Appendix F, two §12-10 terms)

Producer: official-source-researcher (an AI agent). Documents and data only — no rule, no reading of
the text for any lot, no computed figure, no eligibility decision, nothing labelled Verified.
Research and verification (D-093) applied: every official page was opened for THIS pass; each section
number, title and Last Amended date is taken from the page read now, not from the brief or the library.
Worktree `/root/project/nyc-buildability/.claude/worktrees/agent-af20321c166ac7653`; reset to the claim
head `654ea3fade56e075f7bb447eb2f87d0b88fb38a4` on `task/wave24-report-v3` before work.

## REWORK 1 (2026-10-14) — G1 findings F1–F4 (producer: official-source-researcher, AI agent)

Reset to the branch head `11c932b5d0984149868b61de8eb489e840bb53b5` (task/wave24-report-v3, carrying round 1 as
05e4ccb4d). Web = the official host `zoningresolution.planning.nyc.gov` only, one request per resource,
pauses between, no refusal evaded. Nothing labelled Verified; no rule, no reading for a lot, no derived number.

**F1 (REQUIRED) — zr-27-16 top-level outline letters corrected to the print/PDF.** Re-read the section
print/PDF myself: GET `https://zoningresolution.planning.nyc.gov/entityprint/pdf/node/22711` at
2026-10-14T17:26:35Z → HTTP 200, application/pdf, 72,972 bytes, sha256
`1832c6480a9d04b0cb0e1c62465ffaedd9d77e2d849c5cd17744cbe1e7dc56be` (a different render than the round-1
pin `054aacd…`; the PDF is regenerated per request, identical printed letters). `pdftotext -layout`
confirms a single continuous top-level list: (a) Location, (b) Distribution, (c) Bedroom mix, (d) Size,
(e) Records, (f) Restrictive declaration, (g) Housing standards, (h) Insurance, (i) Duration of
obligations, (j) One MIH site, (k) Guidelines. Round 1 had derived the top-level letters from the HTML
`<ol>` markup, which restarts the lettering at "Bedroom mix". Relabelled exactly eight top-level letters
(a→c, b→d, c→e, d→f, e→g, f→h, g→i, h→j); no word, no defined-term marker, no nested label changed.
Recomputed `content_digest_sha256`: `ee3de193…` → `02144575596b2987e0adb70de40fa19eff895dd8b4a32471317dba64346b3ad7`.
Corrected the file's `cross_check.method`, `verbatim_excerpt_composition`, and added a notes entry; corrected
the round-1 Method claim inline (below). Loads through the production loader; digest matches.

**F2 (RENAME) — §12-10 senior term renamed to the official SINGULAR.** The official defined term is
singular "affordable independent residence for seniors". `git mv` of the canonical and the bundled file
`zr-12-10-affordable-independent-residences-for-seniors.snapshot.json` →
`zr-12-10-affordable-independent-residence-for-seniors.snapshot.json`; `snapshot_id` set to the singular to
match the stem; the stale title-discrepancy note updated to record the resolution. The `verbatim_excerpt`
is unchanged (it keeps the ZR's own plural usage inside the definition), so `content_digest_sha256` is
unchanged (`05677e98…`). Grep for the plural id across the repo before editing: it appeared ONLY in this
task's own files — the two snapshot copies (renamed), this producer report (updated), and the task packet
`project-control/tasks/M3-T008.json` (the orchestrator corrects the packet as a scope correction, per the
brief). No rule, test, code, library doc, or other snapshot referenced it, so the rename is safe. No plural
file remains in canonical or bundle.

**F3 (POINTER CAPTURE) — Appendix F written as a pinned pointer.** New file
`docs/research/zr-snapshots/v1/zr-appendix-f.snapshot.json` (+ bundled copy), in the `zr_section_snapshot/v1`
keys (mirrors the accepted `zr-appendix-i` appendix shape; standard 15-key set; the production loader loads
it). Landing page: GET
`…/appendix-f-mandatory-inclusionary-housing-areas-and-former-inclusionary-housing-designated-areas` (node
21424) at 2026-10-14T17:27:19Z → HTTP 200, 330,627 bytes, raw_html_sha256
`f721b91a5eb7e281092ae2e6c0d7d086fd8c5b0a5afc9120fa5619b19c776c61` (byte-identical to round 1's independent
fetch; page title / data-section-number "APPENDIX F – Mandatory Inclusionary Housing Areas and former
Inclusionary Housing Designated Areas"; Last Amended 9/24/2026). Official PDF asset: GET
`…/sites/default/files/appendix/21424/APPENDIX%20F%20%E2%80%93%20…Designated%20Areas.pdf` at
2026-10-14T17:29:54Z → HTTP 200, application/pdf, 10,311,823 bytes, raw_pdf_sha256
`8802b66346f533d75ea351bb237b8333ddce64d754e7762027ee096ef233dd23` (static asset, so sha256 is PINNED,
in `cross_check`). `verbatim_excerpt` = only the prose the landing page prints (heading, the internal
"(9/24/26)" marker, the one-sentence introduction, and the five borough sub-page titles verbatim with the
page's own dash characters); `content_digest_sha256`
`28b7e55ead6d851824f5430f1ea417c6df41c024264a498aea585981d25a8321`. The page body's maps-by-zoning-map
TABLE and the appendix MAPS are NOT transcribed — the notes record that they live in the pinned PDF asset
and the five borough sub-pages, and that nothing is derived. (Supersedes the round-1 "Appendix F — NO FILE
WRITTEN" section below.)

**F4 (per-term Last Amended re-read) — confirmed, no change.** One GET of the §12-10 whole page
`https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10` (node 18523) at 2026-10-14T17:30:16Z
→ HTTP 200, 1,316,687 bytes, sha256 `f2309e6cb1d651290e9a05022c6ad58609226eeb0a8a6fc8130c74b605e797ef`
(byte-identical to round 1). Each term's own article header reads "General Definition | Last Amended |
12/5/2024": AIRS (node 21509) and long-term care facility (node 21590) are both **12/5/2024**, matching the
files' `section_last_amended` 2024-12-05. No date correction needed; the `zr-12-10-long-term-care-facility`
file is byte-unchanged.

**Rework 1 checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, direct exit codes):**
`sync_zr_snapshots.py --check` → EXIT 0 ("200 file(s)"); from services/api, PYTHONPATH set,
`pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/drawings/report/test_report_law_links.py`
→ 28 passed, EXIT 0; from root `tools/research_record_check.py --check` → PASS, EXIT 0;
`scripts/lanes/check_lane_paths.py --coverage` → PASS, EXIT 0 (10402 files). Own self-check over the three
changed/new files (canonical + bundle): loader OK, `content_digest_sha256 == sha256(verbatim_excerpt)`,
`extraction_status` extracted_draft, `raw_html_verified` false, `snapshot_id == stem`, no affirmative
"Verified" label (every occurrence is the negated ADR-007 phrase). No server started; ports 3000/3001/8000
untouched.

**Rework 1 changed-file LF sha256 (`tr -d '\r' < f | sha256sum`; canonical == bundled for each):**
```
zr-27-16.snapshot.json                                        3c1917925717bccd5d7b1f0aa5dfb7427a8793152018ee82e880666792d82bea
zr-12-10-affordable-independent-residence-for-seniors.snapshot.json  9477fb65b89eb90a1d048fd930754267da926b94db58e8bfdf8d536a124ea044
zr-appendix-f.snapshot.json                                   0a7952bd26c7adb509283e67d689e9ad54f16c73870594f61640c16edaa40008
```

## Method (same shape as accepted M5-T163)

For each Chapter-7 section: one direct HTTPS GET of the official HTML (`curl -A Mozilla/5.0`), the
section's own node id read from `data-content-nid`/`data-section-number`, then one GET of its print/PDF
render (`entityprint/pdf/node/<id>` → `print/pdf/node/<id>`). The `verbatim_excerpt` was extracted
PROGRAMMATICALLY from the raw HTML `sec-body`→`field--name-body` container (one block per paragraph /
list item; defined terms `<strong><em>` → `#term#` with the render's inner spacing preserved; outline
labels (a)/(1)/(i) cycling every three `<ol>` depths, matching the print/PDF render; whitespace
normalised, figures omitted, no word changed). `content_digest_sha256 = sha256(verbatim_excerpt)`. Each
excerpt was cross-checked block-by-block against the print/PDF text layer (pdftotext); every block was
found verbatim. **[CORRECTED IN REWORK 1 — G1 finding F1: this holds for the PROSE of every block, but for
zr-27-16 the TOP-LEVEL outline letters were taken from the HTML `<ol>` markup (which RESTARTS the
lettering at "Bedroom mix") and were NOT confirmed against the print/PDF; the official print prints one
continuous list (a) Location … (k) Guidelines. Rework 1 relabelled the eight top-level letters to the
print's glyphs and recomputed that file's digest. The round-1 "outline labels … matching the print/PDF
render" and "every block … verbatim" claims are therefore corrected for zr-27-16's labels. See the
Rework 1 section at the top.]** A pause of a few seconds separated requests; no run of three refusals occurred.
`extraction_status` is `extracted_draft` and `raw_html_verified` is `false` on every file (no
second-agent re-read). For the two §12-10 terms both print/PDF channels were unavailable (documented
DB-167 fallback — see below), so the canonical §12-10 HTML (node 18523, sha256-pinned) is the source.

## Captures (10 files written; each also byte-identical under services/api/app/_zr_snapshots/v1/)

Every section Last Amended **12/5/2024**; HTML channel HTTP 200; PDF channel (sections) HTTP 200
`application/pdf`. "raw_html_sha256" and "raw_pdf_sha256" are the pinned channel digests; the PDF is
regenerated per request (banner "File generated by https://zr.planning.nyc.gov on 10/13/2026"), so the
PDF digest pins the exact render cross-checked.

| snapshot | official title (page) | HTML retrieved | raw_html_sha256 | PDF retrieved | raw_pdf_sha256 | excerpt |
|---|---|---|---|---|---|---|
| zr-27-111 | General definitions | 03:14:44Z | 4a2a99684705026809adc88bb328e7d3f5550f9c1e89b29fbb3c4a3c4d590159 | 03:14:49Z | 7885067fee928232a979ad6b61c9da493c369ad674780e248757511f89d88b8c | 110 blocks / 20712 ch |
| zr-27-131 | Mandatory Inclusionary Housing | 03:14:53Z | 1998957c198c0511fac70af5b7523649d732e88f5709faa0a668ebb702dd66d8 | 03:14:58Z | 374e96d4400bc3c50d0307571fec32cc343b0461f6675534abfefb9f17c887d6 | 16 blocks / 9495 ch |
| zr-27-133 | Mandatory Inclusionary Housing areas | 03:15:05Z | 1df2a97c3336343074cf99a41690fc08eeb83e66d306c28c250e09e4aca8f485 | 03:15:10Z | 3eef83df2ebeedfcd4998a2e3d8f85eaf561bb9c859405752e1036b483243173 | 4 blocks / 929 ch |
| zr-27-14 | Methods of Providing Affordable Housing | 03:15:14Z | b2b53f6f3dbaf895eb8ed5df6209af9ee6b930c04f2ae2149da18529fb9a47fb | 03:15:19Z | f47f2513f60a2ebaad61d447fff749c50760df1205978a643df1a479e794af21 | 10 blocks / 3812 ch |
| zr-27-151 | Additional requirements for MIH developments and UAP developments | 03:15:23Z | cf3e32aef6e313cf62cf52d787b76fee94c5154ed31eb223117efa1a0728183f | 03:15:27Z | 064ac574dbdcaa647ea3e638fbc9302236d7f1223f773b5c2474031885de78c7 | 9 blocks / 3427 ch |
| zr-27-16 | Requirements for MIH Sites or UAP Sites | 03:15:34Z | 4b3d5a8755c85158c27f9638a6969a04fa1ed3f927cfa89680c7701e9a3d4cae | 03:15:39Z | 054aacdb147dd53c598b2b398c21eddb257b4e41bd4cbbaf2e3e97ccc3232c11 | 40 blocks / 9704 ch |
| zr-27-161 | Additional requirements for rental affordable housing | 03:15:46Z | 2967badcec526cc7b43b11d14902d236a52396029192ed0c7443758ec3e6f85b | 03:15:51Z | 8f9684725811d4d91ae3784c829015d7138fbc1598365c78672f7ee9a3ef6ba6 | 32 blocks / 10287 ch |
| zr-27-162 | Additional requirements for homeownership affordable housing | 03:15:57Z | fab14582d1ca903843335db83f9238893d268d9f6a9a4cbb7db53e3d15f4b41c | 03:16:02Z | 00e6518601e9ba1482345567ee3369c35fe684e0c59c50921ba6cd04de7a9245 | 16 blocks / 3588 ch |

Two §12-10 defined terms — source = whole-page §12-10 HTML node 18523, retrieved 2026-10-14T03:21:34Z,
HTTP 200, 1,316,687 bytes, raw_html_sha256 `f2309e6cb1d651290e9a05022c6ad58609226eeb0a8a6fc8130c74b605e797ef`.
Both print/PDF channels unavailable (documented DB-167 fallback): whole-page `entityprint/pdf/node/18523`
→ **HTTP 504** (41-byte "The application did not respond in time.", 03:25:45Z); per-term PDF → **HTTP 403**.

| snapshot | official defined-term title (page) | term node | Last Amended | per-term PDF | excerpt |
|---|---|---|---|---|---|
| zr-12-10-affordable-independent-residences-for-seniors | **affordable independent residence for seniors** (SINGULAR — see discrepancy) | 21509 | 12/5/2024 (General Definition) | 403 @ 03:24:41Z | 4 blocks / 2782 ch |
| zr-12-10-long-term-care-facility | long-term care facility | 21590 | 12/5/2024 (General Definition) | 403 @ 03:24:29Z | 7 blocks / 2305 ch |

### Committed-file sha256 (LF-normalized; canonical == bundled for every file)

```
zr-27-111.snapshot.json                                              81ebf108e8db742fd78e04a7092f06220947b3e03d1184b5b817ef179a44207a
zr-27-131.snapshot.json                                              1e00c2ddd58befd77830dc0d0fb471e6f9b5063c6e1c9b8e0f3d32eb01e4507c
zr-27-133.snapshot.json                                              9357db0f9b656cbdfd9aee851c49031ae3f13c19abf12d7c1a5b70b0f1ba8385
zr-27-14.snapshot.json                                               8dfdafcef431042f72fb20efe1f6d0caaba39d9c4476c144852e0276f4a2a118
zr-27-151.snapshot.json                                              699b1ed8efb2ab4d94b5e60b68327ce35ce7829d253ebdf919bf90802dd56e4b
zr-27-16.snapshot.json                                               39d624db076cce26c1d78a9db7734b8c337dd371f61f2270ec9484e1ad50b39b
zr-27-161.snapshot.json                                              bc5f4b9d79da7ecc0410a9a009a610ac75bb5e9d2d396bb90320ab339b4f269c
zr-27-162.snapshot.json                                              59f6c8e455a5eec152ea63c1f3e72323dfa81544ddb6b3acdd343fdeb7b82422
zr-12-10-affordable-independent-residences-for-seniors.snapshot.json 2e2bfa4a34121bef91e9f46d6edcce9f0f673950072fb36ad787e9d0079a8613 [RENAMED+UPDATED IN REWORK 1 → zr-12-10-affordable-independent-residence-for-seniors.snapshot.json, new LF sha256 9477fb65…; see top]
zr-12-10-long-term-care-facility.snapshot.json                       01e73cd2981b1b3348c751d21ae1ad63fb6ba7a280d45428ef4db5cd9b1bd5a7
```

## Not captured — reported for the orchestrator to correct the packet
**[SUPERSEDED BY REWORK 1 (see top): Appendix F is now captured as a pinned pointer
(zr-appendix-f.snapshot.json, F3), and the §12-10 senior term was renamed to the official singular (F2).
The two items below are the round-1 record.]**

- **Appendix F — NO FILE WRITTEN.** The packet path `/appendix-f` returns **HTTP 404** (57,403 bytes,
  fetched 03:20:03Z). Appendix F does exist and is referenced in the captured text (`27-133`: "…are
  listed in APPENDIX F of this Resolution"), but the official site splits it into a **multi-page
  appendix**, not a single prose section. The current landing page read this pass is node **21424**,
  title (data-section-number) **"APPENDIX F – Mandatory Inclusionary Housing Areas and former
  Inclusionary Housing Designated Areas"**, **Last Amended 9/24/2026**, at
  `/appendix-f-mandatory-inclusionary-housing-areas-and-former-inclusionary-housing-designated-areas`
  (HTTP 200, 330,627 bytes, raw_html_sha256 `f721b91a5eb7e281092ae2e6c0d7d086fd8c5b0a5afc9120fa5619b19c776c61`,
  fetched 03:21:01Z). It has **no `sec-body` container**, carries a table and map images, and links 6
  sub-pages (including an older title family "…Inclusionary Housing Designated Areas and Mandatory
  Inclusionary Housing Areas"). It does not fit the single-file `zr_section_snapshot/v1` prose shape.
  The packet's `/appendix-f` path, its single `zr-appendix-f.snapshot.json` output, and the maps/tables
  content model all need an orchestrator decision (which sub-page(s); whether maps/tables can be a
  section-snapshot at all) before a faithful capture is possible. Nothing was invented.

- **§12-10 "affordable independent residences for seniors" — captured, but TITLE DISCREPANCY flagged.**
  The packet / filename use the **plural** "residences"; the official §12-10 defined-term article read
  this pass is the **singular** "affordable independent residence for seniors" (node 21509). No
  separate plural-titled article exists on the page. The ZR text itself uses the plural inside this very
  definition ("#dwelling units# allocated to #affordable independent residences for seniors#"); the
  defined term is singular. The capture records the exact official singular title in `section_title` /
  `source.defined_term`; `snapshot_id` and filename keep the packet's plural spelling. The file is
  written because the term unambiguously exists and is exactly the senior-housing sub-term the option
  needs; the orchestrator may correct the packet's naming. Flagged in the snapshot `notes[]`.

## ZR 23-154 (re-attempted once; no file)

`https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-154` — one GET through the normal
HTML channel (`curl -A Mozilla/5.0`) at **2026-10-14T03:26:00Z** → **HTTP 403** (57,435-byte HTML error
page). Access remains blocked, matching the first/second passes. No 23-154 snapshot was written; the
block was not worked around (no other user agent, mirror or cache). It stays UNRESOLVED and owed.

## Checks (direct exit codes)

- `python services/api/scripts/sync_zr_snapshots.py --check` → **EXIT 0** ("199 file(s) byte-identical").
- `cd services/api && python -m ruff check .` → **EXIT 0** ("All checks passed!").
- `cd services/api && python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/drawings/report/test_report_law_links.py`
  → **EXIT 0** (28 passed; lanes venv, PYTHONPATH=services/api).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → **EXIT 0** ("10362 file(s), each owned by
  exactly one lane").
- Own self-check (every committed file): `content_digest_sha256 == sha256(verbatim_excerpt)`; the
  production loader `app.rules.snapshots.load_snapshot_file` loads each without error; the excerpt's
  first and last sentence are each found in the raw HTML fetched (whitespace-insensitive) → **ALL PASS,
  10/10**. Block-level PDF cross-check (sections) → every block of every excerpt found verbatim in the
  print/PDF text layer.
- No server started; ports 3000/3001/8000 untouched.

## What I could not check / limitations

- No second-agent re-read of the raw HTML — `raw_html_verified` stays false; `extraction_status`
  `extracted_draft` (every file).
- **PDF text-layer hyphen artifact (sections):** pdftotext intermittently drops the hyphen in section
  cross-references (e.g. "27-10" rendered "2710"). The canonical HTML keeps the hyphen and the stored
  excerpt uses the HTML form; the block cross-check was made hyphen-insensitive and otherwise exact.
  Disclosed in each section's `cross_check.method`.
- **§12-10 terms:** both print/PDF channels unavailable (whole-page 504, per-term 403), so list-item
  labels in the "long-term care facility" definition are MARKUP POSITIONS (the ZR (a)/(1)/(i) scheme),
  not confirmed glyphs (DB-167 F1) — cite items by their words. "affordable independent residence for
  seniors" has no ordered list (all paragraphs), so no label is at issue there.
- **27-16 is a parent section:** its HTML page body (captured here) is the 27-16 parent text only; its
  print/PDF node renders the whole subtree (parent + children 27-161/27-162). The cross-check confirms
  the parent body is present within that render, ending before the 27-161 child header.
- Appendix F not captured and the AIRS singular/plural naming both await an orchestrator packet
  correction (above). 23-154 stays access-blocked and owed.
- A capture changes no result, rule, label or evidence record (D-093). No library doc, evidence record,
  rule, scenario, drawing, test or script was edited; the diff is the 10 canonical snapshots + their 10
  bundled copies + this report only.
