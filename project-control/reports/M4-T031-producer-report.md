# M4-T031 producer report — further law-text captures (D-090 R291; backlog DB-170 item (b))

Producer: legal-corpus-engineer (builder), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a5ad0ce8c33e34fdd`.
Contract/claim head reset to `d952c612a4ff147146c05c66105a9e021928cc71`.
Directive: D-090 R291. This is an AI builder's capture, not a professional or legal review.

Every section and defined-term article below was read by me NOW (2026-10-07) from the official NYC DCP
Zoning Resolution portal (`zoningresolution.planning.nyc.gov`), one request at a time, a few seconds
apart. For a SECTION the authoritative, sha256-and-byte-pinned channel is the section's own canonical
HTML; its own print/PDF render was fetched once and used ONLY as a text check (and as the source of the
printed list-item labels). For a ZR 12-10 DEFINED TERM the authoritative channel is the whole §12-10 page
HTML (node 18523, sha256+byte pinned); the whole-page print/PDF (the completeness channel) returned HTTP
504 (the documented DB-167 behaviour), so the canonical HTML was the channel. Each capture holds official
**source text only**: no rule, no reading of the text for any lot, no derived number.

**38 new canonical files** under `docs/research/zr-snapshots/v1/` (21 sections + 17 ZR 12-10 terms) and 38
byte-identical synced copies under `services/api/app/_zr_snapshots/v1/` (made by
`services/api/scripts/sync_zr_snapshots.py`). No existing capture was edited.
`services/api/tests/rules/test_zr_snapshot_bundle.py` was NOT edited: it discovers captures by directory
glob and names none individually, so the allowed-paths condition for editing it was not triggered.

My extraction method was validated BEFORE capturing: my programmatic extractor reproduces the accepted
committed captures `zr-35-631` (list labels), `zr-23-434` (prose + the cell-by-cell table) and six
committed §12-10 term captures (`residence, or residential`, `lot, corner`, `zoning lot`, `base plane`,
`lot line, rear`, `street line`) **byte-for-byte**, including each `content_digest_sha256`, from the same
official pages read now. The runtime loader (`app/rules/snapshots.py`) recomputed all 110 digests clean
(bundle test, check c).

## 1. The 21 section captures (one file per section)

`content_digest_sha256` = sha256 of the UTF-8 `verbatim_excerpt`. HTML channel is `official_channel: html`;
`raw_html_sha256` + `response_bytes` are the pinned provenance (first 12 of the digest shown). Each
section's own print/PDF returned HTTP 200; its body matched the HTML excerpt word-for-word
(`cross_check.result = match`), EXCEPT the three empty-body container sections (34-23, 23-34, 23-44 — no own
body) and the table sections (prose matched; tables carried cell-by-cell). Each HTML and each PDF request
has its OWN recorded UTC time.

| snapshot_id | § | title (as the page shows it) | node | amended | HTML req (UTC) | PDF req (UTC) | HTML bytes | verbatim bytes | digest (12) |
|---|---|---|---|---|---|---|---|---|---|
| zr-34-22 | 34-22 | Modification of Floor Area Regulations | 18316 | 12/5/2024 | 09:00:41Z | 09:00:44Z | 74140 | 325 | 8f4ad6f49de8 |
| zr-34-221 | 34-221 | Maximum floor area ratio | 18317 | 12/5/2024 | 09:00:48Z | 09:00:51Z | 74773 | 589 | 32320c4a304b |
| zr-34-222 | 34-222 | Change of use | 18318 | 12/5/2024 | 09:00:55Z | 09:00:58Z | 73971 | 292 | 74f7e35a4d62 |
| zr-34-223 | 34-223 | Floor area bonus for a public plaza | 18319 | 12/5/2024 | 09:01:02Z | 09:01:05Z | 74658 | 433 | f3eee67bf9d5 |
| zr-34-224 | 34-224 | Floor area bonus for an arcade | 18320 | 12/5/2024 | 09:01:09Z | 09:01:12Z | 74636 | 420 | 5e4f6e77c093 |
| zr-34-23 | 34-23 | Modification of Yard and Open Area Regulations | 18322 | 12/5/2024 | 09:01:15Z | 09:01:19Z | 73427 | 52 | 4f6975364cc4 |
| zr-34-231 | 34-231 | Modification of front yard requirements | 18323 | 12/5/2024 | 09:01:23Z | 09:01:26Z | 73793 | 160 | df20f8891b07 |
| zr-34-232 | 34-232 | Modification of side yard requirements | 18324 | 12/5/2024 | 09:01:30Z | 09:01:33Z | 74417 | 496 | 9cf83f8d9c3f |
| zr-34-233 | 34-233 | Change of use | 18325 | 12/5/2024 | 09:01:37Z | 09:01:40Z | 73982 | 301 | 0668220dd22e |
| zr-35-641 | 35-641 | Special tower provisions | 18289 | 12/5/2024 | 09:01:43Z | 09:01:47Z | 85747 | 579 | 1d28feb26cb6 |
| zr-35-642 | 35-642 | Special Height and Setback Provisions for Certain Areas | 18296 | 12/5/2024 | 09:01:50Z | 09:01:54Z | 88221 | 2281 | 4d82c16e642a |
| zr-35-643 | 35-643 | Special provisions in other geographies | 22821 | 12/5/2024 | 09:01:57Z | 09:02:00Z | 86537 | 1078 | dcc6dc7b9911 |
| zr-35-22 | 35-22 | Residential Bulk Regulations in C1 or C2 Districts Whose Bulk Is Governed by Surrounding Residence District | 18263 | 12/5/2024 | 09:02:04Z | 09:02:07Z | 86061 | 921 | 6db63c416796 |
| zr-23-34 | 23-34 | Rear Yard and Rear Yard Equivalent Requirements | 22761 | 12/5/2024 | 09:02:11Z | 09:02:14Z | 111156 | 53 | 1cb54ef3763e |
| zr-23-341 | 23-341 | Permitted obstructions in required rear yards or rear yard equivalents | 22762 | 12/5/2024 | 09:02:19Z | 09:02:23Z | 121072 | 6109 | 2cd7b875428b |
| zr-23-311 | 23-311 | Permitted obstructions in all yards, courts and open areas | 22342 | 12/5/2024 | 09:02:26Z | 09:02:30Z | 114122 | 2126 | effc083cce74 |
| zr-23-312 | 23-312 | Additional permitted obstructions generally permitted in all yards | 22343 | 12/5/2024 | 09:02:33Z | 09:02:36Z | 118302 | 4477 | c0475ada314e |
| zr-23-44 | 23-44 | Special Provisions for Certain Areas | 22774 | 12/5/2024 | 09:02:40Z | 09:02:47Z | 111134 | 42 | 6c3a5adc66e3 |
| zr-23-441 | 23-441 | Special tower provisions | 18081 | 12/5/2024 | 09:02:52Z | 09:02:59Z | 124334 | 2640 | d012fd47ce5d |
| zr-23-442 | 23-442 | Special provisions for certain community districts | 18093 | 12/5/2024 | 09:03:03Z | 09:03:10Z | 125668 | 3696 | c6e45275dcb7 |
| zr-23-443 | 23-443 | Special provisions in other geographies | 18097 | 12/5/2024 | 09:03:14Z | 09:03:22Z | 132331 | 2350 | 9bfaedb3409c |

All 21 section pages carry exactly one per-section machine-readable `<time datetime="2024-12-05T12:00:00Z">
12/5/2024</time>` stamp keyed to their `data-section-number`; all are Last Amended 12/5/2024. The print/PDF
bytes are NOT pinned (DB-167 F4): the portal regenerates the PDF per request with the day's date embedded;
observed bytes/sha256 are recorded only under `cross_check.observed_*_nonreproducible`. Each PDF's
"File generated by https://zr.planning.nyc.gov on 10/7/2026" banner and its "LAST AMENDED 12/5/2024" were
read from the PDF and recorded.

## 2. The 17 ZR 12-10 defined-term captures (one file per term)

All extracted from the SAME one whole-§12-10-page HTML fetch (node 18523, HTTP 200, response_bytes
1,316,758, raw_html_sha256 `3c7197026d616c459fd38b3cc76ccc607b7891f600e5a1ec00053ceb8574b5bc`, retrieved
2026-10-07T08:54:21Z — byte-identical to the page the accepted M4-T025/M4-T029 term captures pinned). The
whole-page print/PDF (entityprint/pdf/node/18523) was attempted once at 08:54:31Z and returned HTTP 504 (41
bytes, "The application did not respond in time.") — the documented DB-167 fallback. Each term's per-term
Last Amended stamp and node id are its own; the §12-10 page header shows Last Amended 3/26/2026 (the
most-recently-amended term on the page), recorded as a note, never as a term's provenance.

| snapshot_id | defined term (article title the page shows) | requested as | title form that found it | node | amended | verbatim bytes | digest (12) |
|---|---|---|---|---|---|---|---|
| zr-12-10-yard-rear | yard, rear | rear yard | inverted | 21706 | 12/15/1961 | 77 | 917264446f1a |
| zr-12-10-yard-equivalent-rear | yard equivalent, rear | rear yard equivalent | inverted | 21701 | 12/15/1961 | 126 | 13950498ce5a |
| zr-12-10-yard | yard | yard | exact | 21700 | 9/19/1973 | 492 | 3b8a755c416f |
| zr-12-10-yard-front | yard, front | front yard | inverted | 21702 | 12/15/1961 | 211 | 4f3d63b9a355 |
| zr-12-10-yard-side | yard, side | side yard | inverted | 21707 | 12/15/1961 | 345 | c82d93496979 |
| zr-12-10-lot-coverage | lot coverage | lot coverage | exact | 21595 | 3/22/2016 | 1296 | f5aabef6e32b |
| zr-12-10-curb-level | curb level | curb level | exact | 21544 | 10/25/1993 | 2012 | bd456f6c46c3 |
| zr-12-10-street-wall | street wall | street wall | exact | 21680 | 12/15/1961 | 81 | 0c6534be69d4 |
| zr-12-10-mixed-building | mixed building | mixed building | exact | 21610 | 2/2/2011 | 152 | 6eb9a38952df |
| zr-12-10-residential-equivalent | residential equivalent | residential equivalent | exact | 22726 | 12/5/2024 | 176 | 2332d3ea32b1 |
| zr-12-10-large-site | large site | large site | exact | 22718 | 12/5/2024 | 306 | b066662c437f |
| zr-12-10-qualifying-residential-site | qualifying residential site | qualifying residential site | exact | 22722 | 12/5/2024 | 3455 | 310807a9d82f |
| zr-12-10-dwelling-unit | dwelling unit | dwelling unit | exact | 21550 | 12/5/2024 | 654 | 2987569b30a2 |
| zr-12-10-rooming-unit | rooming unit | rooming unit | exact | 21652 | 12/5/2024 | 224 | 323c44cab3c5 |
| zr-12-10-qualifying-affordable-housing | qualifying affordable housing | qualifying affordable housing | exact | 22721 | 12/5/2024 | 950 | 637b1b09ed49 |
| zr-12-10-qualifying-senior-housing | qualifying senior housing | qualifying senior housing | exact | 22723 | 12/5/2024 | 171 | dba97ae9511f |
| zr-12-10-prevailing-street-wall-frontage | prevailing street wall frontage | prevailing street wall frontage | exact | 22720 | 12/5/2024 | 1310 | 1dbe67004a22 |

### 2.1 How each named term was searched (this is where M4-T029 failed its review)

I first listed ALL 446 defined-term article titles on the §12-10 page. For each of the 17 named terms I
searched the EXACT title, the INVERTED title ("yard, rear" as well as "rear yard"; "yard equivalent, rear"
as well as "rear yard equivalent"), and COMBINED titles that contain the term. Findings:

- **rear yard, rear yard equivalent, front yard, side yard**: the direct-title article is a CROSS-REFERENCE.
  "rear yard" (/node/21640) = `see #yard, rear#`; "rear yard equivalent" (/node/21641) = `see #yard
  equivalent, rear#`; "front yard" (/node/21562) = `see #yard, front#`; "side yard" (/node/21661) = `See
  #yard, side#`. The OPERATIVE definition is in the inverted-title article in each case (nodes 21706, 21701,
  21702, 21707), and that is what is captured; each capture's notes state the cross-reference. (Same pattern
  as the accepted `zr-12-10-lot-corner`, where "corner lot" is a `see lot, corner` cross-reference.) The id
  follows the existing slug rule from the article's OWN title (lowercase, drop commas, spaces→hyphens):
  "yard, rear" → `zr-12-10-yard-rear`, etc.
- **yard** (21700), **lot coverage** (21595), **curb level** (21544), **street wall** (21680),
  **mixed building** (21610), **residential equivalent** (22726), **large site** (22718),
  **qualifying residential site** (22722), **dwelling unit** (21550), **rooming unit** (21652),
  **qualifying affordable housing** (22721), **qualifying senior housing** (22723): each is its own
  exact-title article (distinct from similar titles such as "street wall line", "ancillary dwelling unit",
  "residence district"), captured directly.
- **prevailing street wall frontage** IS defined in ZR 12-10 (exact-title article, /node/22720, Last Amended
  12/5/2024); captured.

All 17 named terms are therefore captured. No named term was reported "not defined".

## 3. Sections found under 34-22, 34-23, 35-64, 23-34, 23-44 (listed from the official pages)

Read from the official chapter contents pages and confirmed by each section's own page:
- **Under 34-22** (Modification of Floor Area Regulations): **34-221** (Maximum floor area ratio), **34-222**
  (Change of use), **34-223** (Floor area bonus for a public plaza), **34-224** (Floor area bonus for an
  arcade). All four captured. 34-22's own body is a short intro paragraph; it is NOT empty.
- **Under 34-23** (Modification of Yard and Open Area Regulations): **34-231** (Modification of front yard
  requirements), **34-232** (Modification of side yard requirements), **34-233** (Change of use). All three
  captured. 34-23 itself is a heading/container: its `div.sec-body` is EMPTY (no own body); captured as
  header-only with that stated, `cross_check.result = no_own_body`.
- **Under 35-64**: **35-641** (Special tower provisions), **35-642** (Special Height and Setback Provisions
  for Certain Areas), **35-643** (Special provisions in other geographies). All three captured (35-64 itself
  was captured by M4-T029 and is NOT recaptured).
- **Under 23-34** (Rear Yard and Rear Yard Equivalent Requirements): **23-341** (Permitted obstructions in
  required rear yards or rear yard equivalents), 23-342, 23-343, 23-344. 23-341 captured; 23-342/343/344 were
  already captured by M4-T029 and are NOT recaptured. 23-34 itself is a heading/container with an EMPTY
  `div.sec-body`; captured header-only (`no_own_body`).
- **Under 23-44** (Special Provisions for Certain Areas): **23-441** (Special tower provisions), **23-442**
  (Special provisions for certain community districts), **23-443** (Special provisions in other geographies).
  All three captured. 23-44 itself is a heading/container with an EMPTY `div.sec-body`; captured header-only
  (`no_own_body`).
- **35-22** is a leaf section (no sections numbered under it: the chapter shows 35-20, 35-21, 35-22, 35-23,
  35-24). **23-311 and 23-312** are leaf sections (siblings 23-313 exists but is not named by this task and
  is not captured).

## 4. Tables — captured cell by cell (23-434 precedent)

Three section captures contain HTML `<table>`s. Each table is NOT inlined in `verbatim_excerpt`; its place
is a placeholder and the table is carried cell-by-cell in a structured field read directly from the HTML
`<td>` cells (the authoritative source order).

- **23-441** and **23-442**: one clean 2-column, 12-row table each ("Percent of #lot coverage# of the tower
  portion" / "Minimum percent of total #building# #floor area# distribution below the level of 150 feet";
  40.0-or-greater→55.0…30.0-to-30.9→60.0 for 23-441, …45.0…50.0 for 23-442). Carried in the `table` field
  (columns + row_count + rows with cell_footnotes); placeholder "[table - see structured `table` field]".
- **23-443**: TWO tables, carried in a `tables` array (placeholders "[table 1 of 2 …]" / "[table 2 of 2 …]").
  Table 1 = the Limited-Height-District table (5 rows, 2 cols; LH-1→50 feet, LH-lA→60 feet, LH-2→70 feet,
  LH-3→100 feet). Table 2 = "TRANSITION AREA DIMENSION AND MAXIMUM HEIGHT", a merged/spanning-cell table
  recorded ROW BY ROW in source order (cell counts vary by row where the source spans cells; no columns/rows
  split imposed); its "45*" cells carry a LITERAL "*" (a footnote marker, source text), and the footnote
  text is in a `footnotes` field keyed "*".
- **Quirk preserved exactly**: the Limited-Height cell reads **"LH-lA"** (a lower-case letter l, not a
  digit 1) on BOTH the HTML `<td>` and the print/PDF; captured verbatim as "LH-lA".
- **pdftotext cross-check of tables**: I confirmed every WORD of every table cell appears in the section's
  print/PDF (0 words missing across all three sections). The squashed-string containment fails only for the
  long/header cells because `pdftotext -layout` interleaves the wrapped lines of adjacent columns — the
  cosmetic layout artifact M4-T029 disclosed for 34-112. The HTML `<td>` cell order is authoritative and is
  what the structured fields record.

## 5. The one list-bearing §12-10 term — labels are MARKUP POSITIONS (DB-167 F1)

Sixteen of the 17 term definitions contain NO ordered list (`<ol>`); any (a)/(b)/(c) in them is LITERAL
source text (e.g. "qualifying affordable housing" lists (a) #MIH developments#…; those (a)/(b)/(c) are
literal). **`zr-12-10-qualifying-residential-site` is the one exception**: its definition DOES contain a
three-level ordered list ((a)/(b)/(c) → (1)-(4) → (i)-(iv)). Because the whole-page print/PDF returned HTTP
504 AND the per-term print/PDF (entityprint/pdf/node/22722) returned HTTP 403 (attempted once, 2026-10-07T09:09:42Z,
57,524-byte HTML error page), there is NO glyph-authoritative channel for this term's list markers. Its
labels are therefore recorded as POSITIONS IN THE PAGE'S MARKUP (the HTML ordered-list nesting; the Zoning
Resolution standard letter/number/lower-roman scheme), NOT confirmed printed labels — stated plainly in that
capture's `cross_check.method`, composition note and notes. All section list labels, by contrast, are
confirmed against each section's own print/PDF (which returned 200).

## 6. What was NOT captured, and why

- The further sections the new texts point to (section 7 below) marked "no" — outside this task's named set;
  listed, not captured.
- 23-342, 23-343, 23-344 (under 23-34) and 35-64 — already captured by M4-T029; NOT recaptured.
- 23-313 (a sibling under 23-31) — not named by this task; not captured.
- The §12-10 defined terms the new texts USE beyond the 17 named (e.g. #block#, #Commercial District#,
  #wide street#, #narrow street#, #lot area#, #base plane#, #story#, #Greater Transit Zone#, #Outer Transit
  Zone#, #mass transit stations#, #short dimension of a block#, #UAP developments#, #MIH developments#,
  #affordable independent residences for seniors#, #long-term care facilities#,
  #transportation-infrastructure-adjacent frontage#, #multiple dwelling residences#, #income index#,
  #income band#, #restrictive declaration#, #affordable housing regulatory agreement#, #households#,
  #guidelines#) — §12-10 terms not in this task's named set; listed, not captured.

Everything named by the task is captured.

## 7. Every further section / defined term the new texts point to (LISTED, not captured)

Section references in the 21 new section texts (pointing words ≤25; "captured?" checked against all 110
snapshots now in the store):

| section | pointed-to from | pointing words | already captured? |
|---|---|---|---|
| 23-20 | 34-22 | "#floor area# and #open space# regulations as set forth in Section 23-20 (FLOOR AREA REGULATIONS), inclusive" | No |
| 23-22 | 34-223, 34-224 | floor-area bonus cross-refs | Yes (zr-23-22) |
| 23-311 | 23-312, 23-341, 34-232 | "obstructions set forth in Section 23-311" | Yes (captured here) |
| 23-312 | 23-341, 34-232 | "obstructions set forth in … Section 23-312" | Yes (captured here) |
| 23-381 | 23-443 | "where a #building# adjoining a #public park# utilizes the provisions of Section 23-381" | No |
| 23-41 / 23-411 / 23-412 | 23-341, 23-442 | permitted-obstruction / penetration cross-refs | Yes (zr-23-41/411/412) |
| 23-42 / 23-43 | 23-443, 35-642 | yard / height-and-setback cross-refs | Yes |
| 23-431 / 23-432 / 23-434 / 23-435 | 23-441, 23-442, 23-443, 35-641 | street-wall / height-setback / eligible-site / tower cross-refs | Yes |
| 23-441 / 23-442 | 35-641, 35-642 | tower-provision cross-refs | Yes (captured here) |
| 23-62 | 23-312, 23-341 | "Balconies, unenclosed … subject to the applicable provisions of Section 23-62" | No |
| 25-621 / 25-622 | 23-312 | "subject to the provisions of Section 25-621 … and Section 25-622 (Location of parking spaces …)" | No |
| 25-85 | 23-341 | "excluded from #floor area# pursuant to Section 25-85 (Floor Area Exemption)" | No |
| 26-50 | 23-312 | "subject to the applicable provisions of Section 26-50 (SPECIAL SCREENING AND ENCLOSURE PROVISIONS)" | No |
| 34-11 | 34-22 | "made applicable to such districts in Section 34-11 (General Provisions)" | Yes (zr-34-11) |
| 34-223 / 34-224 | 34-221 | "except as provided for in … Section 34-223 … Section 34-224" | Yes (captured here) |
| 35-631 / 35-632 / 35-641 | 35-642, 35-643 | street-wall / height-setback cross-refs | Yes (631/632 earlier; 641 here) |
| 37-70 | 34-223 | "#public plaza# provided in accordance with the provisions of Section 37-70, inclusive" | No |
| 37-80 | 34-224 | "#arcade# provided in accordance with the provisions of Section 37-80 (ARCADES)" | No |

Section references in the one list-bearing TERM (`qualifying residential site`): **23-21** ("the #floor area
ratio# provisions for #qualifying residential sites# in Section 23-21 (Floor Area Regulations for R1 Through
R5 Districts)") — No; **66-11** ("#mass transit stations#, as defined in Section 66-11 (Definitions)") — No;
**27-111** ("as those terms are defined in Section 27-111 (General definitions)") — No.

Article/Chapter pointers (whole chapters, not section numbers; not captured): **Article II, Chapter 3** —
from 34-221 ("the … #floor area ratio# permitted pursuant to the provisions of Article II, Chapter 3, except
as provided for in the following Sections") and from 35-22 ("shall apply for the purposes of applying the
provisions of Article II, Chapter 3, and the remaining provisions of this Chapter").

Plain-text references (not section numbers), pointed to, not captured: "the New York City Administrative
Code", "the Multiple Dwelling Law" (via `rooming unit`), "HPD … #guidelines#".

Defined terms the new texts use are Article I / §12-10 terms. Of them, these now HAVE a §12-10 capture: the
17 captured here plus the earlier-captured `floor area`, `floor area ratio` (as part of the floor-area
capture), `lot area`, `zoning lot`, `base plane`, `street line`, the lot-line/lot-width/lot-depth family,
`Manhattan Core`, `residence, or residential`, `qualifying exterior wall thickness`, and `Special Downtown
Brooklyn District`. The many others used (section 6) are not in this task's named set.

## 8. Checks — each with its DIRECT exit code

Run from `services/api` with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
pytest `-p no:cacheprovider` (checks a–c) and from the repo root (check d). `echo $?` immediately after each
command (never piped through `tail`).

a. `python -m ruff check .` → "All checks passed!" — **exit 0**
b. `python scripts/sync_zr_snapshots.py --check` → "OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (110 file(s))." — **exit 0** (run after `sync_zr_snapshots.py` write, which synced the 38 new copies)
c. `python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/rules/test_zoning_rule_review_register.py` → "50 passed in 1.18s" — **exit 0** (the bundle's default-store load recomputed all 110 content digests clean)
d. from repo root: `python3 scripts/lanes/check_lane_paths.py --coverage` → "LANE COVERAGE PASS: 9013 file(s), each owned by exactly one lane." — **exit 0**; `python3 tools/modularity_check.py --check` → "selected 716 files; failures 0; warnings 29" (all 29 warnings are pre-existing production files I did not touch; no capture file is handwritten production source) — **exit 0**
e. `git diff --name-status d952c612a4ff147146c05c66105a9e021928cc71..HEAD -- docs/research/zr-snapshots/v1` → 38 added (`A`) files only; recorded in the producer RETURN after the commit.

I did NOT run the full `services/api` pytest suite — the orchestrator runs it once at the wave's final
candidate.

## 9. Scope and the no-bend rules

Changes are confined to allowed paths: 38 new canonical capture files under
`docs/research/zr-snapshots/v1/`, their 38 byte-identical synced copies under
`services/api/app/_zr_snapshots/v1/`, and this report. No existing capture, rule file, rule engine,
registry, review register, reference case, plan, helper-research file, other test, dependency file,
`.claude/**`, or any other `project-control/**` file was edited. No new package. No value is shown anywhere
because of a capture. Each capture holds source text only (`extraction_status: extracted_draft`,
`raw_html_verified: false`); nothing here is a Verified zoning determination (ADR-007: a rule later citing a
capture ships under the standing not-professionally-reviewed label with a direct source link; professional
review is advisory).

## 10. Doubt / limitations disclosed

- `zr-12-10-qualifying-residential-site` list labels are markup positions, not confirmed printed labels
  (both PDF channels unavailable: whole-page 504, per-term 403) — section 5, DB-167 F1. Cite its items by
  their words.
- The table cells of 23-441/442/443 are read from the authoritative HTML `<td>`s; the per-cell
  cross-check against the print/PDF is word-level (0 words missing) because `pdftotext -layout` interleaves
  wrapped header/long cells (cosmetic) — section 4.
- The 27 new texts have NOT been independently read for any lot (that is DB-170 item (a), task M4-T030) and
  no second agent has re-read these captures (`raw_html_verified: false`).

END-OF-REPORT
