# M4-T034 producer report — law-text captures behind the owner's reviewer's check (source text only)

Producer: legal-corpus-engineer (builder), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-aaeee5c99a231537c`.
Contract/claim head reset to `d8ad46a85b31923f5eee4553543b3f2e1a6eb22b`.
Directive: D-090 R291, R513, R516, R517, R526. This is an AI builder's capture, not a professional or
legal review. SOURCE TEXT ONLY: no statement of what any text means for any lot, no verdict on whether
the reviewer is right; no rule, reference case, register entry, record or result changed.

Every target below was read by me NOW (2026-10-07) from the official NYC DCP Zoning Resolution portal
`zoningresolution.planning.nyc.gov` only, one request per page, a pause (~4 s) between requests. The
tracking-tagged `zr.planning.nyc.gov?utm_source=chatgpt.com` links in the amendment were NOT fetched.

## Method and extractor validation

Channels follow the accepted M4-T031/T033 method. For a SECTION the authoritative, sha256-and-byte-pinned
channel is the section's own canonical HTML (`field--name-body`); its own print/PDF (HTTP 200) is a
text check and the completeness cross-check. For a ZR 12-10 DEFINED TERM the authoritative channel is the
whole-page §12-10 HTML (node 18523, sha256 and byte count pinned, byte-identical to the accepted zr-12-10
captures); the whole-page print/PDF (`entityprint/pdf/node/18523`) returns HTTP 504 and the per-term PDF
returns HTTP 403 (the documented DB-167 fallback), so term list-marker glyphs are not glyph-confirmed.

**Extractor validated before capturing:** my stdlib-only extractor reproduces the committed
`zr-12-10-floor-area` (defined term with 4-deep nested lists) and `zr-23-20` (section) **byte-for-byte**
(content-digest match), and reproduces the committed `zr-23-432` height table cell-for-cell (R6B row
30/45/55/45/65). Re-fetched pages are byte-identical to the accepted captures' pins (23-20 sha256
`60a643b0…`, §12-10 sha256 `3c719702…`), confirming the source is byte-stable since M4-T033.

## 23 new captures (one file each) + 23 byte-identical synced copies

New canonical files under `docs/research/zr-snapshots/v1/`; synced copies under
`services/api/app/_zr_snapshots/v1/` by `scripts/sync_zr_snapshots.py`. No existing capture edited or
re-fetched in place. `tests/rules/test_zr_snapshot_bundle.py` NOT edited (it discovers by directory glob
and names no id). IDs:

- Target 1 (4): `zr-35-30`, `zr-35-31`, `zr-35-32`, `zr-35-33`.
- Target 2 (4): `zr-12-10-fully-electrified-building`, `zr-12-10-ultra-low-energy-building`,
  `zr-12-10-building`, `zr-12-10-story`.
- Target 3 (1): `zr-23-24`.
- Target 4 (14): `zr-25-02`, `zr-25-20`, `zr-25-211`, `zr-25-221`, `zr-25-231`, `zr-25-80`, `zr-25-81`,
  `zr-25-811`, `zr-36-21`, `zr-36-31`, `zr-36-62`, `zr-36-70`, `zr-36-71`, `zr-36-711`.

## Per target — found/not, with the number and title the SITE shows

### (1) Mixed-building floor-area section of Article III, Chapter 5 — FOUND; lead 35-31 borne out
The reviewer's lead `35-31` IS borne out: the site shows **35-31 "Maximum Floor Area Ratio"**
(/node/18266, Last Amended 12/5/2024), whose body carries the shared-floor-area attribution paragraph
("Where #floor area# in a #building# is shared by multiple #uses#, the #floor area# for such shared
portion shall be attributed to each #use# proportionately, based on the percentage each #use# occupies
of the total #floor area# of the #zoning lot# less any shared #floor area#"). 35-31 is NOT a parent; the
site shows it as a leaf under parent **35-30 "APPLICABILITY OF FLOOR AREA AND OPEN SPACE REGULATIONS"**
(/node/18265, header-only, children 35-31 … 35-362). The sibling sections that state how mixed-building
floor areas combine are **35-32 "Maximum Floor Area for Mixed Buildings on Qualifying Residential Sites"**
(/node/22820, one table) and **35-33 "Maximum Floor Area and Special Provisions for Mixed Buildings or
Zoning Lots With Multiple Buildings Containing Community Facility Use in Certain Districts"**
(/node/18267, tables). Captured `zr-35-30` (header, children list), `zr-35-31`, `zr-35-32`, `zr-35-33`.
Channel: HTML authoritative + section print/PDF text-check (all HTTP 200, word/cell match). Related
section 35-24 ("Applicability of Residential Bulk Rules to Non-residential Portions of Mixed Buildings",
/node/22817) was found but concerns bulk (height/setback) applicability, not floor-area combination —
listed, not captured.

### (2) ZR 12-10 definitions behind the energy exclusion — ALL FOUND (searched three ways)
The 'floor area' definition's exclusion item (15) excludes 5% of floor area within a `#fully electrified
building#` or `#ultra low energy building#` (existing capture `zr-12-10-floor-area`). Each term searched
exact-title, inverted/comma-title and combined-title against the 484 defined-term titles on the §12-10
page:
- **fully electrified building** /node/22338 (Last Amended 12/6/2023) — exact title; no inverted variant.
  Captured `zr-12-10-fully-electrified-building`. Rests on `#building#`; eligibility also turns on being
  a building "existing on December 6, 2023" and on Local Law 154 of 2021 (external statute, not a ZR term).
- **ultra low energy building** /node/22341 (Last Amended 12/6/2023) — exact title; no inverted variant.
  Captured `zr-12-10-ultra-low-energy-building`. Rests on `#building#` and `#stories#` (three-stories-or-
  less threshold) and on external standards (Local Law 154 of 2021, NYC Energy Conservation Code, NYC
  Building Code). "net-zero energy building" is NOT a defined term (descriptive phrase; only `#building#`
  is marked) — searched, absent, not captured.
- Defined terms the two rest on that were NOT captured yet: **building** /node/21521 (2/2/2011) and
  **story** /node/21675 (2/2/2011). Captured `zr-12-10-building`, `zr-12-10-story`.

LABEL CAVEAT (disclosed in `zr-12-10-ultra-low-energy-building`): that definition's own internal
cross-references name "paragraph (a)", "paragraph (b)(2)" and "paragraph (d)", which shows the official
printed top-level labels are (a),(b),(c),(d) and the second-level labels numeric — NOT the arabic/roman
markup positions the excerpt carries. The glyph-authoritative PDF channel is unavailable (504/403); item
TEXT is verbatim; cite items by their words. `zr-12-10-building`'s (a)–(g) labels are LITERAL source text
(no HTML `<ol>`); `fully electrified building` and `story` are single paragraphs.

### (3) Section ZR 23-20 points to for certain areas — FOUND: 23-24
`zr-23-20` (existing) states "Special rules governing certain areas are set forth in Section 23-24." The
site shows **23-24 "Special Provisions for Certain Areas"** (/node/22752, Last Amended 12/5/2024), a
header-only parent with children **23-241 "Special tower provisions", 23-242 "Special provisions for
certain community districts", 23-243 "Existing public amenities for which floor area bonuses have been
received"**. Captured `zr-23-24` (header, children list). Lead borne out.

### (4) Parking, loading and bicycle — the sections that say WHETHER a requirement applies
Residential off-street parking in a Residence District lives in **Article II, Chapter 5**; the current
(City of Yes, 12/5/2024) structure is BY TRANSIT ZONE, not by R-district band:
- **25-02 "Applicability"** (/node/17516, 4/22/2009) — general applicability of permitted/required
  parking and bicycle parking. Captured `zr-25-02`.
- **25-20 "REQUIRED ACCESSORY OFF-STREET PARKING SPACES FOR RESIDENCES"** (/node/17540, 12/5/2024) —
  the requirement, routing to 25-21/25-22/25-23 by transit zone. Captured `zr-25-20`.
- **25-211 "General provisions"** (Inner Transit Zone; /node/17541) — "no #accessory# off-street parking
  spaces shall be required for #dwelling units# or #rooming units# created after December 5, 2024."
  Captured `zr-25-211`. (Parent 25-21 is header-only.)
- **25-221 "General provisions"** (Outer Transit Zone; /node/22798) — parking required per 25-222.
  Captured `zr-25-221`.
- **25-231 "General provisions"** (Beyond Greater Transit Zone; /node/17545) — parking required per
  25-232. Captured `zr-25-231`. (Parents 25-22, 25-23 are header-only.)

LEAD/EXPECTATION DISCREPANCY (parking waiver/reduction "on a small lot or for a small number of spaces"):
the site shows the residential requirement sections 25-221/25-231 allow reduction/elimination of required
spaces only pursuant to **73-432, 73-433, 74-52** (income-restricted / qualifying-senior-housing /
special-permit reductions, in Article VII) — NOT a small-lot / small-number waiver. The Inner Transit
Zone (25-211) requires no residential parking at all. The small-lot / below-minimum / mixed-use waivers
(25-33, 25-36, 25-37) sit under the NON-residential subchapter 25-30 and are listed, not captured.

Bicycle parking (Article II, Chapter 5): **25-80 "BICYCLE PARKING"** (/node/17612, 12/5/2024) states
WHETHER the bicycle provisions apply (to developments; enlargements increasing floor area ≥50%;
conversions; new dwelling units after 4/22/2009; certain parking facilities). Captured `zr-25-80`. The
reviewer's lead **25-811** IS borne out: the site shows **25-811 "Enclosed bicycle parking spaces"**
(/node/17614, 12/5/2024) with the requirement TABLE giving the required amount per `#use#`, under parent
**25-81 "Required Bicycle Parking Spaces"** (/node/17613, header-only). Captured `zr-25-81`, `zr-25-811`.

Commercial-district counterparts (Article III, Chapter 6): **36-21 "General Provisions"** (/node/17903,
12/5/2024, five requirement tables) — commercial / community-facility required parking (local retail
uses); **36-31 "General Provisions"** (/node/17914, 12/5/2024) — required parking for residences when
permitted in Commercial Districts (routes to 25-20 by transit zone); **36-62 "Required Accessory
Off-street Loading Berths"** (/node/17974, 12/5/2024, two tables). Captured `zr-36-21`, `zr-36-31`,
`zr-36-62`. Commercial bicycle counterpart: **36-70 "BICYCLE PARKING"** (/node/17986, 2/2/2011,
applicability), **36-71 "Required Bicycle Parking Spaces"** (/node/17987, header-only), **36-711
"Enclosed bicycle parking spaces"** (/node/17988, 12/5/2024, requirement table). Captured `zr-36-70`,
`zr-36-71`, `zr-36-711`. Channels: HTML authoritative + section print/PDF text-check (all HTTP 200).

Group (4) count = 14 captures (≤ 20). See "found, not captured" below.

## (5) The reviewer's statements of law, against the section and capture (NO verdict)

| Reviewer statement (source-055) | Section the site shows | Capture (id) holding the text |
|---|---|---|
| Shared floor area allocated proportionately among uses (23-20 and 35-31) | 23-20 FLOOR AREA REGULATIONS; 35-31 Maximum Floor Area Ratio | `zr-23-20` (existing); `zr-35-31` (new) |
| Amenity 5% base = the building's residential floor area (23-231) | 23-231 | `zr-23-231` (existing) |
| Two energy routes: fully electrified (existing 12/6/2023) vs ultra-low-energy (new, performance + professional verification) | ZR 12-10 'fully electrified building'; 'ultra low energy building' | `zr-12-10-fully-electrified-building` (new); `zr-12-10-ultra-low-energy-building` (new) |
| 5% energy floor-area exclusion; qualifying-wall exclusion | ZR 12-10 'floor area' exclusion items (12),(15); 'qualifying exterior wall thickness' | `zr-12-10-floor-area` (existing); `zr-12-10-qualifying-exterior-wall-thickness` (existing) |
| R6B 45-ft max base height, setbacks above, 55/65-ft overall | 23-432 (R6B row: min base 30, standard max base 45 / max bldg 55; qualifying max base 45 / max bldg 65); setback 23-433 | `zr-23-432` (existing); `zr-23-433` (existing) |
| Dwelling-unit factors by housing kind (29 / 35; 680 factor; senior none) | Message links at 23-22; the repository's current-text capture has the dwelling-unit factor at 23-52 | `zr-23-22` (existing); `zr-23-52` (existing) |
| Bicycle requirements vary by use and building configuration | 25-81 / 25-811 (and commercial 36-71 / 36-711) | `zr-25-81`, `zr-25-811` (new); `zr-36-71`, `zr-36-711` (new) |
| Parking, loading and bicycle applicability must be resolved | 25-02, 25-20, 25-211/221/231; 36-21, 36-31, 36-62; 25-80/36-70 | the group-(4) captures above |

No statement of the message is marked "not found": each rests on text now held in a capture (new or
existing). No verdict is drawn on whether any statement is correct.

## Found beyond the bound of group (4) — "found, not captured" (number and title)
- Article II Ch 5 residential parking: 25-021/022/023/024 (applicability sub-sections); 25-212, 25-222,
  25-232 (the per-transit-zone calculation detail / design standards); 25-24 "Special Provisions for
  Certain Areas" + 25-241; non-residential parking 25-30…25-37 incl. **25-33 "Waiver of Requirements for
  Spaces Below Minimum Number", 25-36 "Waiver of Requirements for Certain Small Zoning Lots", 25-37
  "Waiver for Mixed-Use Developments"**; off-street loading 25-70…25-77; bicycle detail 25-812, 25-82
  "Authorization for Reduction of Spaces", 25-83, 25-84, 25-85 "Floor Area Exemption", 25-86 "Waiver or
  Reduction of Spaces for Subsidized Housing".
- Article III Ch 6: 36-20 (parent), 36-211, 36-22, 36-23 "Waiver … Below Minimum Number", 36-24, 36-25
  "Waiver for Certain Small Zoning Lots or Establishments", 36-26; 36-30 (parent), 36-32, 36-33; loading
  36-60 (parent), 36-61, 36-63, 36-64, 36-65, 36-66x; bicycle 36-712, 36-72 "Authorization for Reduction
  of Spaces", 36-73, 36-74, 36-75, 36-76.
- Residential parking reductions the requirement sections point to (Article VII; not captured):
  73-432, 73-433, 74-52.

## Further sections the new texts point to that are NOT captured
25-21, 25-212, 25-22, 25-222, 25-23, 25-232, 25-83, 25-85 (from 25-xx parking/bicycle); 35-36 (from
35-31); 36-23, 36-24, 36-25, 36-30, 36-53, 36-73, 36-75 (from 36-xx); 62-43, 73-44, 75-31 (from 36-62
loading / special-permit cross-refs); 73-432, 73-433, 74-52 (reductions, above). ZR 12-10 defined terms
the new texts name but outside this task's set (each has its own §12-10 entry; none captured): e.g.
`#development#`, `#enlargement#`, `#dwelling unit#`, `#rooming unit#`, `#group parking facilities#`,
`#conversions#`, `#fire walls#`, `#primary entrance#`, `#lot lines#`, `#residential equivalent#`,
`#Inner/Outer/Greater Transit Zone#`, `#commercial#`, `#community facility#`.

## Channels that did not answer
- §12-10 whole-page print/PDF `entityprint/pdf/node/18523` → **HTTP 504** (41-byte timeout body); per-term
  PDFs → **HTTP 403** (57,524-byte error page). The documented DB-167 fallback; the four term captures use
  the sha256-pinned §12-10 HTML and disclose this.
- All 19 section print/PDFs returned **HTTP 200**. For `zr-36-21` the PDF text-check is PARTIAL: pdftotext
  does not extract a few styled table cells (e.g. the use-categories "Libraries, museums or non-commercial
  art galleries", "Riding academies or stables"); those cells ARE present in the sha256-pinned HTML (the
  authoritative channel) and are captured cell-by-cell. Disclosed in that capture's `cross_check.result`.

## Checks — each with its DIRECT exit code
Run with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest
`-p no:cacheprovider`; checks a–c from `services/api`, check d from repo root. Exit read directly.
- a. `python -m ruff check .` → "All checks passed!" — **exit 0**
- b. `python scripts/sync_zr_snapshots.py --check` → "OK: runtime-bundled ZR snapshots are byte-identical
  to the canonical source (156 file(s))." — **exit 0** (133 prior + 23 new)
- c. `python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py
  tests/rules/test_zoning_rule_review_register.py` → "50 passed" — **exit 0**
- d. from repo root: `python3 scripts/lanes/check_lane_paths.py --coverage` → "LANE COVERAGE PASS: 9270
  file(s), each owned by exactly one lane." — **exit 0**
- e. `git status --porcelain` → 46 added (`??`) = 23 under `docs/research/zr-snapshots/v1/` + 23 under
  `services/api/app/_zr_snapshots/v1/`; after commit `git diff --name-status <contract-head> HEAD` =
  **46 added (`A`)** + **1 modified (`M`)** = this report (a pre-seeded placeholder now filled in, an
  allowed path). No existing capture, and no file outside allowed paths, modified or deleted; the bundle
  test is NOT edited. I did NOT run the full `services/api` pytest suite (the orchestrator runs it once at
  the wave's final candidate).

## Scope and the no-bend rules
Changes confined to allowed paths: 23 new canonical captures, their 23 byte-identical synced copies, and
this report. No existing capture, rule, rule engine, registry, review register, reference case, plan, other
test, dependency file, `.claude/**`, or any other `project-control/**` file edited; the parallel builders'
areas (`services/api/app/scenario/three_answers/`, `docs/measurement-basis/`) untouched. No new package.
Each capture holds source text only (`extraction_status: extracted_draft`, `raw_html_verified: false`);
nothing here is a Verified zoning determination (ADR-007). No reading of any text for any lot; no verdict
on the reviewer's statements.

## Doubt / limitations disclosed
1. `zr-12-10-ultra-low-energy-building` list labels are markup positions, NOT confirmed printed glyphs
   (§12-10 PDF unavailable, 504/403); the definition's own cross-references show the real labels are
   (a)–(d) with numeric sub-items. Item TEXT is verbatim; cite by words.
2. `zr-36-21` PDF text-check is partial (pdftotext drops some styled cells); HTML is authoritative and
   carries every cell. The five requirement tables are large; a qualified reviewer should confirm the
   cell grid against the page.
3. `zr-36-70(b)` preserves a SOURCE markup anomaly verbatim: the official HTML serves "within a ##building
   by 50 percent" (an empty `<strong><em></em></strong>` span, written `##`, then an unwrapped "building");
   25-80(b) serves the same provision as `#building#`. Kept exactly as served; disclosed in the capture.
4. retrieved_at records the session time (2026-10-07); the reproducible provenance is each page's pinned
   sha256 + byte count (the re-fetch matched the accepted captures' pins, confirming byte-stability).
5. No capture has been independently re-read by a second agent (`raw_html_verified: false`); the
   independent reading of these texts is a later task. None of these texts has been interpreted for any lot.

END-OF-REPORT
