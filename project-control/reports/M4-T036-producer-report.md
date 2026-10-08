# M4-T036 producer report - further law-text captures named as missing by the step-P5 readings (source text only)

Producer: legal-corpus-engineer (builder), an AI agent (not a professional or legal review), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-aa4e2f81bc91cedd9`.
Contract/claim head reset to `599f9b0ca0540212f3cdd670d1a4eb4aed78e093`.
Directive: D-090 R291, R517, R526; backlog DB-188. SOURCE TEXT ONLY: no statement of what any text means for
any lot, no verdict on whether a reading is right; no rule, reference case, register entry, record or result
changed. Every page was read by me NOW (2026-10-08) from `zoningresolution.planning.nyc.gov` only, one direct
HTTPS GET per page (`curl -A Mozilla/5.0`), a pause between requests; no `utm_source`-tagged link was fetched.

## Method and extractor validation

Channel follows the accepted M4-T031/T033/T034 method. The authoritative, sha256-and-byte-pinned channel is each
section's own canonical HTML `field--name-body` (`raw_html_sha256` + `response_bytes` pinned). The section's own
print/PDF (HTTP 200) is used ONLY as a text check (`cross_check`); its PDF bytes are NOT pinned (the portal
regenerates them per request - M4-T025 F4 / DB-167). Tables are captured cell-by-cell from the HTML.

My stdlib-only extractor reproduces the committed `zr-35-31` capture's `verbatim_excerpt` **byte-for-byte**
(content-digest match), and reproduces the committed `zr-25-221` / `zr-23-434` prose byte-for-byte. One observed
difference from yesterday's captures is disclosed: the portal now renders ordered-list labels by nesting depth
`(a)/(b)...` then `(1)/(2)...` then `(i)/(ii)...` (confirmed in both the HTML-derived output and today's print/PDF);
yesterday's `zr-25-221` used `(1)/(2)` for its one depth-0 list. I captured today's rendering; I did not edit the
existing capture. The raw page HTML carries a per-render Drupal `form_build_id` token in the site search form, so
the whole-page `raw_html_sha256` can drift between sessions while the section body is byte-stable; the reproducible
semantic pin is `content_digest_sha256` over `verbatim_excerpt` (disclosed in every capture's notes).

`content_digest_sha256 == sha256(verbatim_excerpt)` for all 29 captures (the loader enforces this; the bundle test
loaded all 185 snapshots green).

## 29 new captures (one file each) + 29 byte-identical synced copies

New canonical files under `docs/research/zr-snapshots/v1/`; synced copies under
`services/api/app/_zr_snapshots/v1/` by `scripts/sync_zr_snapshots.py`. No existing capture edited or re-fetched in
place. `tests/rules/test_zr_snapshot_bundle.py` NOT edited (it discovers by glob, names no id).

Count by group: (1) 6, (2) 3, (3) 12, (4) 2, (5) 4, (6) 2 = **29**.

| Capture id | Title the site prints | Node | Address (path) | Form | Table | Last Amended | PDF text-check |
|---|---|---|---|---|---|---|---|
| zr-33-10 | FLOOR AREA REGULATIONS | 17719 | /article-iii/chapter-3/33-10 | heading-only | - | 12/15/1961 | no_own_body |
| zr-33-11 | Definitions | 17720 | /article-iii/chapter-3/33-11 | leaf | - | 11/19/1987 | match |
| zr-33-12 | Maximum Floor Area Ratio | 17721 | /article-iii/chapter-3/33-12 | leaf (own body + children) | - | 12/5/2024 | match |
| zr-33-121 | In districts with bulk governed by Residence District bulk regulations | 17722 | /article-iii/chapter-3/33-121 | leaf | 1 | 12/5/2024 | match |
| zr-33-122 | Commercial buildings in all other Commercial Districts | 17723 | /article-iii/chapter-3/33-122 | leaf | 1 | 12/5/2024 | partial (1 cell) |
| zr-33-123 | Community facility buildings or buildings used for both community facility and commercial uses in all other Commercial Districts | 17724 | /article-iii/chapter-3/33-123 | leaf | 1 | 12/5/2024 | partial (2 cells) |
| zr-23-241 | Special tower provisions | 18021 | /article-ii/chapter-3/23-241 | leaf | - | 12/5/2024 | match |
| zr-23-242 | Special provisions for certain community districts | 22755 | /article-ii/chapter-3/23-242 | leaf | - | 12/5/2024 | match |
| zr-23-243 | Existing public amenities for which floor area bonuses have been received | 18022 | /article-ii/chapter-3/23-243 | leaf | - | 12/5/2024 | match |
| zr-25-212 | Existing parking requirements in the Inner Transit Zone | 22797 | /article-ii/chapter-5/25-212 | leaf | 1 | 12/5/2024 | partial (2 cells) |
| zr-25-22 | Required Parking in the Outer Transit Zone | 17544 | /article-ii/chapter-5/25-22 | heading-only | - | 12/5/2024 | no_own_body |
| zr-25-222 | Requirements for developments or enlargements in the Outer Transit Zone | 22799 | /article-ii/chapter-5/25-222 | leaf | 1 | 12/5/2024 | partial (6 cell / 1 prose) |
| zr-25-23 | Required Parking Beyond the Greater Transit Zone | 22800 | /article-ii/chapter-5/25-23 | heading-only | - | 12/5/2024 | no_own_body |
| zr-25-232 | Requirements for developments or enlargements beyond the Greater Transit Zone | 22801 | /article-ii/chapter-5/25-232 | leaf | 1 | 12/5/2024 | partial (11 cells) |
| zr-36-23 | Waiver of Requirements for Spaces Below Minimum Number | 17905 | /article-iii/chapter-6/36-23 | intro body + children | - | 12/15/1961 | match |
| zr-36-231 | In districts with high, medium or low parking requirements | 17906 | /article-iii/chapter-6/36-231 | leaf | 1 | 6/6/2024 | match |
| zr-36-232 | In districts with very low parking requirements | 17907 | /article-iii/chapter-6/36-232 | leaf | - | 6/6/2024 | match |
| zr-36-233 | Exceptions to application of waiver provisions | 17908 | /article-iii/chapter-6/36-233 | leaf | - | 6/6/2024 | match |
| zr-36-24 | Waiver of Requirements for All Zoning Lots Where Access Would Be Forbidden | 17909 | /article-iii/chapter-6/36-24 | leaf | - | 4/14/2010 | match |
| zr-36-25 | Waiver for Certain Small Zoning Lots or Establishments | 17912 | /article-iii/chapter-6/36-25 | leaf | - | 12/5/2024 | match |
| zr-36-30 | REQUIRED ACCESSORY OFF-STREET PARKING SPACES FOR RESIDENCES WHEN PERMITTED IN COMMERCIAL DISTRICTS | 17913 | /article-iii/chapter-6/36-30 | heading-only | - | 12/15/1961 | no_own_body |
| zr-66-11 | Definitions | 21928 | /article-vi/chapter-6/66-11 | leaf | - | 8/14/2025 | match |
| zr-appendix-i | APPENDIX I (the site prints no subtitle; data-section-title is empty) | 21238 | /appendix-i | maps + boundary text | - (maps block) | 11/21/2024 | partial (maps are images) |
| zr-73-432 | Reduction of existing parking spaces for income-restricted housing units | 18852 | /article-vii/chapter-3/73-432 | leaf | - | 12/5/2024 | match |
| zr-73-433 | Reduction of existing parking spaces for qualifying senior housing | 18853 | /article-vii/chapter-3/73-433 | leaf | - | 12/5/2024 | match |
| zr-74-52 | Special Permit to Remove Required Parking | 19122 | /article-vii/chapter-4/74-52 | leaf | - | 12/5/2024 | match |
| zr-75-31 | Authorization to Remove Required Parking | 22840 | /article-vii/chapter-5/75-31 | leaf | - | 12/5/2024 | match |
| zr-32-161 | Use Group VI – general use allowances | 22487 | /article-iii/chapter-2/32-161 | leaf | 2 | 6/6/2024 | partial (styled symbols) |
| zr-32-131 | Use Group III – general use allowances | 22456 | /article-iii/chapter-2/32-131 | leaf | 2 | 12/5/2024 | partial (styled symbols) |

Every section number named in the objective exists on the site AT that number, with the title above. No number was
missing or moved; nothing was captured under a guessed number.

## Group notes (word-for-word where a sentence states what a text says)

- **Group (1).** 33-10 "FLOOR AREA REGULATIONS" is heading-only; the contents page lists its children 33-11, 33-12,
  33-13, 33-14, 33-15, 33-16. 33-12 "Maximum Floor Area Ratio" is NOT heading-only - the site shows an operative
  body and the child sections 33-121, 33-122, 33-123, 33-124. 33-121 is captured; the site titles it "In districts
  with bulk governed by Residence District bulk regulations"; its opening reads: "In the districts indicated, for a
  #zoning lot# containing a #commercial# or #community facility# #use#, the maximum #floor area ratio# is determined
  by the #Residence District# within which such #Commercial District# is mapped and shall not exceed the maximum
  #floor area ratio# set forth in the following table:". 33-121/122/123 FAR tables captured cell-by-cell. No reading
  for any lot is drawn.
- **Group (2).** 23-241, 23-242, 23-243 captured, each with the title above; the header 23-24 (existing capture
  `zr-23-24`) is NOT edited or re-fetched.
- **Group (3).** 25-212/222/232 captured with their tables cell-by-cell. 25-22 and 25-23 are heading-only (children
  25-221/222 and 25-231/232; 25-221 and 25-231 are the existing captures `zr-25-221`/`zr-25-231`, not re-fetched).
  36-23 shows a short applicability body - "In all districts, as indicated, the requirements for #accessory#
  off-street parking spaces shall be subject to the waiver provisions of this Section." - and its waiver provisions
  are in its children 36-231, 36-232, 36-233, all captured. 36-24 and 36-25 captured. 36-30 is heading-only; its
  child 36-31 is the existing capture `zr-36-31` and is NOT duplicated.
- **Group (4).** 66-11 "Definitions" captured; it defines "mass transit station": "For the purposes of this
  Chapter, "mass transit station" shall refer to any subway or rail #mass transit station# operated by a #transit
  agency#. ...". "select mass transit station" was searched three ways in 66-11 - exact ("select mass transit
  station(s)"), inverted ("mass transit station, select"), combined - with 0 hits; it is NOT defined in 66-11. It
  IS a defined term in ZR 12-10 (portal node 22727, defined-term entry "select mass transit stations"), used by the
  already-captured §12-10 "Outer Transit Zone" definition; it is not in this task's capture set and is not captured
  here. **APPENDIX I form:** the page is a list of map IMAGES (one key map plus fifteen numbered transit-zone maps,
  Maps 1-15) with one textual boundary paragraph. I captured the text verbatim - "The boundaries shown on the maps
  in this APPENDIX include:", "all of Manhattan Community Districts 9, 10, 11 and 12;", "all of Bronx Community
  Districts 1, 2, 4, 5, 6 and 7; and", "all of Brooklyn Community Districts 1, 2, 3, 4, 6, 7, 8, 9 and 16.",
  "Portions of other Community Districts are shown on Maps 1 through 15 in this APPENDIX." - plus the fifteen map
  captions and the image URLs (in the `maps` block). The transit-zone BOUNDARIES themselves are raster map images
  and CANNOT be captured as text, so a lot's Inner/Outer/Greater Transit Zone value is a RECORDED value, not a
  reading (the §12-10 transit-zone definitions also route the boundary to the Department of City Planning's ZoLa
  "Transit Zones Parking Geographies" layer).
- **Group (5).** 73-432 (income-restricted), 73-433 (qualifying senior), 74-52 (special permit), 75-31
  (authorization) captured, each with the title above. No verdict on when a reduction applies to any lot.
- **Group (6).** 32-161 "Use Group VI – general use allowances" (two tables, captions "USE GROUP VI – RETAIL TRADE
  ESTABLISHMENTS" and "USE GROUP VI – SERVICE ESTABLISHMENTS") and 32-131 "Use Group III – general use allowances"
  (two tables, "USE GROUP III(A) – COMMUNITY FACILITIES WITH SLEEPING ACCOMMODATIONS" and "USE GROUP III(B) –
  COMMUNITY FACILITIES WITHOUT SLEEPING ACCOMMODATIONS") captured cell-by-cell. The columns the site shows are
  "Uses (NAICS Code)" (32-161) / "Uses" (32-131), then "C1 C2 C3 C4 C5 C6 C7 C8", then "PRC". **The use tables carry
  a PRC (Parking Requirement Category) column and NO loading requirement category column.** The PRC letter-to-ratio
  parking tables are in the existing capture `zr-36-21`; the required loading berths are in the existing capture
  `zr-36-62` (neither re-fetched). The styled permission symbols (● ♦ ○ – S P U, per the in-table legend) are not
  reliably extracted by pdftotext, so the cross-check is partial and the HTML is authoritative.

## Sections that do not exist as named / were not captured, with the reason
- None of the named sections was missing or moved. Siblings deliberately left "found, not captured" (reported, not
  guessed): 33-124 (Existing public amenities ...), 33-13, 33-14, 33-15 (with 33-151/152), 33-16; 25-24 (Special
  Provisions for Certain Areas) with 25-241; 36-26 (Waiver for Mixed-use Developments); 36-32, 36-33 (children of
  36-30); the §12-10 defined term "select mass transit stations" (node 22727, defined in §12-10, not in 66-11).

## Pages that needed the fallback channel
- None. All 29 section/appendix HTML pages and all 29 print/PDFs returned HTTP 200; no 504/403 fallback was needed.
  Partial PDF text-checks (disclosed in each capture's `cross_check.result` and notes) are: the FAR tables
  33-122/123 and the parking tables 25-212/222/232 (a few styled/line-wrapped cells pdftotext drops), and the Use
  Group tables 32-161/32-131 (styled permission symbols pdftotext drops). In every case the HTML is authoritative
  and the cells are captured cell-by-cell.

## What each new capture still points to that is NOT captured (from the captured text's own cross-references)
- zr-33-11 -> 12-10. zr-33-12 -> 33-13, 33-14, 33-15, 33-16. zr-33-121 -> 74-902, 12-10, 24-111, 74-903. zr-33-123
  -> 24-111, 34-112, 74-903. zr-23-241 -> 23-435, 12-10. zr-23-242 -> 23-21. zr-23-243 -> 37-727, 74-761. zr-25-212
  -> 25-211, 25-20, 25-63. zr-25-222 -> 25-63. zr-25-232 -> 25-63. zr-36-231 -> 36-233, 36-27, 36-21, 36-22.
  zr-36-232 -> 36-233, 36-21, 36-22. zr-36-233 -> 36-23. zr-36-24 -> 36-21, 36-22, 36-53. zr-36-25 -> 36-21, 12-10.
  zr-66-11 -> 12-10. zr-73-433 -> 25-20. zr-74-52 -> 25-20. zr-75-31 -> 25-20. zr-32-161 -> 32-10, 44-45, 48-49.
  zr-32-131 -> 32-10. (zr-33-10, zr-33-122, zr-25-22, zr-25-23, zr-36-23, zr-36-30, zr-73-432, zr-appendix-i carry
  no in-body section cross-reference of their own.) Each capture lists its own "points to" set in its notes; no ZR
  12-10 defined terms used by these texts are captured here.

## Checks - each with its DIRECT exit code
Run with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`;
a-c from `services/api`, d from the repo root. Exit read directly (`echo $?`), never piped through `tail` first.
- a. `python -m ruff check .` -> "All checks passed!" - **exit 0**
- b. `python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/rules/reference_cases`
  -> "78 passed in 1.29s" - **exit 0** (the bundle test loaded and digest-validated all 185 snapshots)
- c. `python scripts/sync_zr_snapshots.py --check` -> "OK: runtime-bundled ZR snapshots are byte-identical to the
  canonical source (185 file(s))." - **exit 0** (156 prior + 29 new)
- d1. (repo root) `python tools/modularity_check.py --check` -> "selected 724 files; failures 0; warnings 29"
  (all 29 warnings pre-existing in other modules; this task adds data files only) - **exit 0**
- d2. (repo root) `python3 scripts/lanes/check_lane_paths.py --coverage` -> "LANE COVERAGE PASS: 9413 file(s), each
  owned by exactly one lane." - **exit 0**
- e. `git status --porcelain` -> 58 added (`??`) = 29 under `docs/research/zr-snapshots/v1/` + 29 under
  `services/api/app/_zr_snapshots/v1/`; after commit `git diff --name-status <claim-head> HEAD` = **58 added (`A`)**
  + **1 modified (`M`)** = this report (a seeded placeholder now filled, an allowed path). No existing capture, and
  no file outside allowed paths, modified or deleted; the bundle test is NOT edited. I did NOT run the full
  `services/api` pytest suite (the orchestrator runs it once at the wave's final candidate).

## Scope and the no-bend rules
Changes confined to allowed paths: 29 new canonical captures, their 29 byte-identical synced copies, and this
report. No existing capture, rule, rule engine, registry, review register, reference case, plan, measurement-basis
file, other test, dependency file, `.claude/**`, or any other `project-control/**` file edited; the parallel
builder's areas (`docs/measurement-basis/`, `services/api/tests/scenario/measurement_basis/`) untouched. No new
package. Each capture holds source text only (`extraction_status: extracted_draft`, `raw_html_verified: false`);
nothing here is a Verified zoning determination (ADR-007). No reading of any text for any lot; no verdict.

## Doubt / limitations disclosed
1. The portal renders ordered-list labels by nesting depth `(a)/(1)/(i)`; I captured today's rendering, which
   differs from the committed `zr-25-221`'s `(1)/(2)` for a depth-0 list. I did not edit the existing capture.
2. `raw_html_sha256`/`response_bytes` pin THIS session's whole-page fetch; the page's non-body chrome carries a
   per-render Drupal `form_build_id`, so a reviewer re-fetching on a later day may see a different whole-page
   digest while the section body is byte-stable. The reproducible semantic pin is `content_digest_sha256` over
   `verbatim_excerpt` (the extractor reproduces `zr-35-31` byte-for-byte).
3. Per-request PDF bytes are not reproducible (DB-167); the PDF is a text check only and its sha256 is not pinned.
4. The Use Group tables (32-161/32-131) are large symbol tables; the HTML is authoritative and every cell is
   captured, but a qualified reviewer should confirm the symbol grid against the page.
5. `retrieved_at` records a representative session time (2026-10-08); the reproducible provenance is each capture's
   pins and its `content_digest_sha256`. No capture has been independently re-read by a second agent
   (`raw_html_verified: false`); the independent reading of these texts into the R6B reference cases is a later task.

END-OF-REPORT
