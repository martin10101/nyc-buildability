# M4-T026 producer report — law-text captures for a residential building in a commercial overlay (work-order step P2, gap K9)

Producer: legal-corpus-engineer (builder), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a13d667e91665f5c0`.
Contract/claim head reset to `8dd39c9f0d2c09bc596063eaf259dc658f29b1c5`.
Directive: D-090 R291. This is an AI builder's capture, not a professional or legal review.

All eight sections were read by me NOW from the official NYC DCP Zoning Resolution portal
(`zoningresolution.planning.nyc.gov`), one request at a time, a few seconds apart. The HTML is the
authoritative, sha256-and-byte pinned channel; each section's own print/PDF render was fetched once
and used ONLY as a text check (and as the source of the printed list-item labels — see "Labels" and
finding F1 below). Each capture holds official **source text only**: no rule, no reading of the text
for any lot, no derived number.

## 1. The eight captures (one file per section)

New canonical files under `docs/research/zr-snapshots/v1/`; byte-identical synced copies under
`services/api/app/_zr_snapshots/v1/` (made by `services/api/scripts/sync_zr_snapshots.py`).

| snapshot_id | § | title (as the page shows it) | article/ch | amended | verbatim bytes (UTF-8) | content_digest_sha256 |
|---|---|---|---|---|---|---|
| zr-34-11 | 34-11 | General Provisions | III / 4 | 12/5/2024 | 359 | e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc |
| zr-34-111 | 34-111 | Residential bulk regulations in Cl or C2 Districts whose bulk is governed by surrounding Residence District | III / 4 | 12/5/2024 | 880 | 5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf |
| zr-34-24 | 34-24 | Modification of Height and Setback Regulations | III / 4 | 12/5/2024 | 1250 | 0cc3f02617a47639611221737cd0cc7ebfec8a7754346a212e6af88fdfa55630 |
| zr-35-53 | 35-53 | Modification of Rear Yard Requirements | III / 5 | 12/5/2024 | 637 | 755aa5113e8ea050c21e41355448ed20d88610eeaadaea256a92c23611629ceb |
| zr-35-63 | 35-63 | Height and Setback Requirements in Commercial Districts with R6 Through R12 Equivalency | III / 5 | 12/5/2024 | 798 | 77ff1923e3d3607202964541eb29e714b7cbaa9ab6dde7ddd9ccfbbd032ebe72 |
| zr-35-631 | 35-631 | Street wall location | III / 5 | 12/5/2024 | 4511 | 816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9 |
| zr-35-632 | 35-632 | Maximum height of buildings and setback regulations | III / 5 | 12/5/2024 | 1769 | 8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10 |
| zr-35-633 | 35-633 | Additional height and setback provisions | III / 5 | 12/5/2024 | 626 | 4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3 |

(`content_digest_sha256` = sha256 of the UTF-8 `verbatim_excerpt`; the runtime loader
`app/rules/snapshots.py` recomputes and fails closed on any mismatch — it loaded all 45 files clean.)

## 2. Provenance per capture — address, channel, the time of EACH request (F2), amendment

Each request's own UTC time is recorded separately (not one rounded time for all — M4-T025 finding F2).

HTML channel (`official_channel: html`; sha256 + byte count are the pinned provenance):

| § | request_url (HTML) | node | HTTP | request time (UTC) | response_bytes | raw_html_sha256 | Last Amended |
|---|---|---|---|---|---|---|---|
| 34-11 | …/article-iii/chapter-4/34-11 | 18310 | 200 | 2026-10-07T05:08:49Z | 74179 | 4735404f32a4175b35e6dd3fa44a038e94f0d06879cca39b74373d469c728e0c | 12/5/2024 |
| 34-111 | …/article-iii/chapter-4/34-111 | 18311 | 200 | 2026-10-07T05:11:38Z | 74800 | c0df9f95ec75c832c2018d7ae0bd8bcc4c2399e5f0f6a0b0e3d5099144f22d20 | 12/5/2024 |
| 34-24 | …/article-iii/chapter-4/34-24 | 18326 | 200 | 2026-10-07T05:13:26Z | 75612 | 077ad8f151b3a2a9c6e065434f06bead782651f687dcb63ebb6e1ad539e5b8cb | 12/5/2024 |
| 35-53 | …/article-iii/chapter-5/35-53 | 18281 | 200 | 2026-10-07T05:15:39Z | 85787 | 798dd20a63b466b3f693d82fd3ec4e2a263d0739d70a39f98dd1dbaa2881580a | 12/5/2024 |
| 35-63 | …/article-iii/chapter-5/35-63 | 18290 | 200 | 2026-10-07T05:15:57Z | 86164 | 2244240970d9c86319ecf726481411544883c63babff6939270c0ffad1699911 | 12/5/2024 |
| 35-631 | …/article-iii/chapter-5/35-631 | 18291 | 200 | 2026-10-07T05:17:06Z | 91638 | 646f31f03e2b868d6ebe3f926100f3b4fdf43164c47eb461b50940066f08db78 | 12/5/2024 |
| 35-632 | …/article-iii/chapter-5/35-632 | 18292 | 200 | 2026-10-07T05:17:23Z | 87541 | 00aa237548e93bc2a207a5a89fb3c9755ce9a7ac2c3997c2fd5f06cb7b727bb4 | 12/5/2024 |
| 35-633 | …/article-iii/chapter-5/35-633 | 22824 | 200 | 2026-10-07T05:17:32Z | 85894 | 68ff431c012d8e40cf8f2142d5f2333081591194a4b38dfbc22135bc5a9d9aac | 12/5/2024 |

Each page carries exactly one per-section machine-readable stamp
`<time datetime="2024-12-05T12:00:00Z">12/5/2024</time>` inside the section's own `.amended` block
whose amendment-history popup is keyed `data-section-number="<§>"` — so the stamp belongs to that
section (not a sibling). No dedicated section page exposed a separate site-wide currency banner.

print/PDF channel (`role: text_check_only`) — treated as a TEXT CHECK, bytes NOT pinned (F4):

| § | print_pdf request_url → final_url | node | HTTP | request time (UTC) | observed bytes (non-reproducible) | observed sha256 (non-reproducible) | result |
|---|---|---|---|---|---|---|---|
| 34-11 | entityprint/pdf/node/18310 → print/pdf/node/18310 | 18310 | 200 | 2026-10-07T05:09:55Z | 55506 | 90e9dd1f5d05fa55a163d9f3294a4251072055897d5d7c0670f668ea269eda16 | match |
| 34-111 | …/node/18311 | 18311 | 200 | 2026-10-07T05:13:10Z | 47651 | e77120dfb9d999b25fb2d47f20774a5053ba02b80c185e617602a707bb9e73e9 | match |
| 34-24 | …/node/18326 | 18326 | 200 | 2026-10-07T05:13:52Z | 50987 | e876e3daf013bcec3a4cc8f802440a13a61df470cc40083a89c7f3fab8e3973f | match |
| 35-53 | …/node/18281 | 18281 | 200 | 2026-10-07T05:15:46Z | 47403 | 60c6aa882fbea9aa09c9536efca73f63211f0863e235f0468b0e4c2d2840f2f3 | match |
| 35-63 | …/node/18290 | 18290 | 200 | 2026-10-07T05:16:24Z | 62634 | 76eed879b6beeba930e9f65fcc01a7fb0e8a2f291b8c231ae39d797613562be5 | match |
| 35-631 | …/node/18291 | 18291 | 200 | 2026-10-07T05:18:10Z | 54626 | d88d97ca713c3b586b5b789d149a4dc50d075c8f9c5939396818c0467951dd27 | match |
| 35-632 | …/node/18292 | 18292 | 200 | 2026-10-07T05:18:18Z | 51047 | 5716ae8fa4f4e380dd7f47d059712b67a091f3eab1e7a14626227c5f6ae6f35a | match |
| 35-633 | …/node/22824 | 22824 | 200 | 2026-10-07T05:18:24Z | 47734 | c43052f6f3d94192cb1fb68ef8e9431f4dbbab887e0588db8f30f32ee2f1896a | match |

**F4 applied:** the portal regenerates the PDF on every request with that request's generation date
embedded (every PDF banner read "File generated by https://zr.planning.nyc.gov on 10/7/2026"), so the
PDF bytes/sha256 are NOT reproducible. In every capture `cross_check.raw_pdf_sha256 = null`; the
observed bytes/sha256 are recorded only under `observed_*_nonreproducible` for transparency. The
operative fact is `cross_check.result = match`: the print/PDF body equals the HTML excerpt word-for-word
(whitespace and pdftotext hyphenated line-wraps normalised on both sides). Each `pdf_last_amended`
read "LAST AMENDED 12/5/2024".

Two of the print nodes render a whole FAMILY (same behaviour the accepted M4-T025 23-23 capture
documented): node 18310 (34-11) prints 34-11 + 34-111 + 34-112 + 34-113; node 18290 (35-63) prints
35-63 + 35-631 + 35-632 + 35-633. Each such capture holds ONLY its own section's body; the note in the
file states this. The six leaf nodes (18311, 18326, 18281, 18291, 18292, 22824) print only their own
section.

## 3. Labels — taken from the print/PDF text (F1 applied)

For every ordered list, the HTML renders the item markers as CSS (there is NO label glyph in the HTML
page text). So the labels in each `verbatim_excerpt` are the labels the section's **own print/PDF**
prints in front of each item, confirmed by reading that PDF's text; where no list exists there is no
label. This is the M4-T025 finding-F1 practice: a label that is not printed in the page's text is
taken from the print/PDF and that is stated; I did not need the "position in the markup" fallback for
any section because every print/PDF answered (none 504'd).

- 34-11: no list.
- 34-111: `(a)`, `(b)`.
- 34-24: `(a)`, `(b)`; under `(b)`: `(1)`, `(2)`, `(3)`.
- 35-53: no list.
- 35-63: no list.
- 35-631: `(a)`; under `(a)`: `(1)`, `(2)`; then `(b)`, `(c)`, `(d)`.
- 35-632: `(a)`, `(b)`, `(c)`.
- 35-633: `(a)`, `(b)`.

## 4. Sections found under 35-63

35-63's own print/PDF (node 18290) renders exactly these sections, and 35-63's own body names the
first three plus sibling 35-64: **35-631** (Street wall location), **35-632** (Maximum height of
buildings and setback regulations), **35-633** (Additional height and setback provisions). All three
are captured. (35-64 is a sibling section at the 35-6x level, NOT a child numbered under 35-63; it is
listed as pointed-to, not captured.) No 35-634 or any further 35-63x child exists on the page.

## 5. Do the named paragraphs exist as named?

- **`34-24(b)(1)` — EXISTS as named.** In the official print/PDF of 34-24, paragraph `(b)` ("In
  Commercial Districts with R6 through R12 equivalency") contains sub-item `(1)`: "the modifications to
  #residential# height and setback regulations set forth in Section 35-63, inclusive, shall be
  applied;". The HTML renders `(a)/(b)/(1)/(2)/(3)` as CSS list markers with no glyph in the page text;
  the print/PDF prints them. **This DIFFERS from the helper lead and from DISCOVERY_BACKLOG DB-166,
  which state `34-24(b)(1)` does NOT exist as named — see the lead comparison in §6; the difference is
  that the lead read the HTML channel only.**
- **`35-631(b)` — EXISTS as named.** Paragraph `(b)` "Percentage-based rules": "At least 70 percent of
  the #aggregate width of street walls# shall be located within eight feet of the #street line#…"
  (labels `(a)/(b)/(c)/(d)` printed in the print/PDF). Matches the rule file's "35-631(b) … within 8 ft
  of the street line".
- **`35-632(a)` — EXISTS as named.** Paragraph `(a)` "Height and setback requirements": minimum/maximum
  base height and maximum building height per the table in §23-432, setback per §23-433 (labels
  `(a)/(b)/(c)` printed in the print/PDF). Matches the rule file's "35-632(a) (heights)".

## 6. Each capture beside the helper's lead — EVERY difference (none resolved silently)

The lead (`docs/research/helper-research/P2_Article_III_Lead_2026-10-07.md`) read five pages (HTML
only, 03:55–03:59 UTC, no print/PDF) and did NOT open 34-11 or 35-63. It is a lead, never a source;
the captures are from my own fetches. HTML byte counts the lead reported equal my fetches exactly
(34-111 74,800; 34-24 75,612; 35-53 85,787; 35-631 91,638; 35-632 87,541), consistent with unchanged
pages read at different times.

- **34-11 (not in the lead).** The lead listed 34-11 only as "pointed to; not checked further" and gave
  no node. I captured it: node 18310, amended 12/5/2024, body = district list "C1 C2 C3 C4 C5 C6" + two
  paragraphs routing residential-building bulk to Article II Ch 3 "except as modified by the provisions
  of Sections 34-21 through 34-24". No contradiction; this is a first reading.
- **34-111.** Lead title and node (18311) match; the lead flagged the page renders "Cl or C2" (a
  lowercase `l`, a font/glyph artifact for "C1") — **confirmed: the official `<h3>` and
  `data-section-title` literally contain "Cl or C2"; I captured the title verbatim as shown.** Content
  (R1–R5 → R5 bulk; R1/R2 → R3-2 bulk) matches. **Difference:** the lead said the two sub-items "are not
  lettered in the body text; they are ordered-list items"; the authoritative print/PDF PRINTS `(a)` and
  `(b)`, which I assigned (F1). The lead's HTML observation is not wrong (the HTML has no glyphs); the
  print/PDF adds the confirmed labels.
- **34-24 — the material difference.** Lead (and DB-166): "34-24 has no lettered paragraphs at all (no
  (a)/(b), no (b)(1)); so 34-24(b)(1) does not exist as named." **My finding from the official print/PDF:
  the section PRINTS `(a)`, `(b)`, and under `(b)` the items `(1)`, `(2)`, `(3)`; therefore `34-24(b)(1)`
  EXISTS as named** (it is the R6–R12 routing to §35-63, inclusive). Root cause of the lead's conclusion:
  it read the HTML channel only, where the labels are CSS-rendered. Title ("Modification of Height and
  Setback Regulations"), node (18326) and pointers (34-11, 35-62, 35-63, 36-64, 35-71) match. Not resolved
  silently: this correction is stated here and in §5; the rule-file note / DB-166 is a rules task's
  concern, not changed by this capture task.
- **35-53.** Lead title, node (18281), "no lettered paragraphs", scope words "for a residential portion
  of a mixed building", and pointer to 23-41 all match my capture. No difference.
- **35-63 (not in the lead).** The lead did not open 35-63 (its doubt #5 asked the capture task to
  enumerate the children). **Difference/resolution:** 35-63 (node 18290) has three children — 35-631,
  35-632 AND **35-633** — the lead knew only the first two; I enumerated and captured 35-633.
- **35-631.** Lead title ("Street wall location"), node (18291) and structure (four paragraphs (a)
  Line-up / (b) Percentage-based / (c) large zoning lots / (d) Articulation, with (a) carrying a nested
  sub-list) match. Lead: paragraph (b) exists as named — confirmed (§5). The lead inferred the letters
  from the text's internal cross-references; I additionally confirmed the PRINTED labels `(a)/(1)/(2)/(b)/(c)/(d)`
  from the print/PDF. No contradiction.
- **35-632.** Lead title ("Maximum height of buildings and setback regulations"), node (18292), three
  subdivisions ((a) heights / (b) modifications on eligible sites / (c) tower regulations) and pointers
  (23-43 inclusive, 23-432, 23-433, 23-434, 23-435) match. **Difference:** the lead was unsure whether
  "(a)" is printed ("The body does not print a literal '(a)'; the letter is the list position. The
  capture task should confirm the letter at the source."). The print/PDF confirms `(a)/(b)/(c)` ARE
  printed; I assigned them from it (F1).
- **35-633 (not in the lead).** Entirely new vs the lead: "Additional height and setback provisions",
  node 22824, amended 12/5/2024. **Note:** unlike the other 35-63x sections it prints NO district-
  applicability list line; its body begins with the stem "The additional height and setback regulations
  set forth in Section 23-436 shall apply, except as follows:" then items `(a)`, `(b)`. Captured as the
  page shows it.

## 7. Pointed-to sections and defined terms (LISTED, not captured by this task)

Extracted from each captured body (section links + "Section NN-NN" mentions + bold-italic defined
terms). "Captured?" is against the repository's snapshot store (the 37 prior + these 8).

Sections the captured texts point to:

| section | pointed-to from | pointing words (≤25) | already captured? |
|---|---|---|---|
| 34-21 | 34-11 | "except as modified by the provisions of Sections 34-21 through 34-24" | No |
| 35-62 | 34-24 | "(a) … the modifications … set forth in Section 35-62 shall be applied" | No |
| 36-64 | 34-24 | "(b)(2) the special height and setback provisions for certain areas set forth in Section 36-64" | No (Article III, Ch 6) |
| 35-71 | 34-24 | "(b)(3) where the optional bulk regulations for sky exposure plane buildings are utilized … Section 35-71, inclusive" | No |
| 23-41 | 35-53 | "shall be permitted, pursuant to Section 23-41 (Permitted Obstructions), inclusive" | No (23-42 is captured; 23-41 is not) |
| 35-64 | 35-63 | "Additional height and setback provisions are set forth in Section 35-633 and Section 35-64, inclusive" | No (sibling, not a 35-63 child) |
| 23-431 | 35-631, 35-633 | "the line-up provisions of paragraph (a) of Section 23-431 may be applied" | Yes (zr-23-431) |
| 23-432 | 35-631, 35-632 | "the maximum base height and before the required setback as set forth in Section 23-432" / table in 23-432 | Yes (zr-23-432) |
| 23-43 | 35-632 | "the height and setback regulations of Section 23-43 … inclusive, shall be applied" | No as a unit (umbrella; 23-431/432/433 captured) |
| 23-433 | 35-632 | "a setback shall be provided … in accordance with Section 23-433" | Yes (zr-23-433) |
| 23-434 | 35-632 | "(b) for zoning lots meeting the criteria of paragraph (a) of Section 23-434 … table in Section 23-434" | No |
| 23-435 | 35-632 | "(c) towers shall be permitted pursuant to the provisions of Section 23-435" | No |
| 23-436 | 35-633 | "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows" | No |

Plain-text references (not section numbers): "Article II, Chapter 3" (in 34-11, 34-111, 34-24) and
"this Chapter" = Article III Chapter 4 (in 34-111) — pointed to, not captured as units.

Defined terms the captured texts use (all defined in Article I / §12-10 etc.; **none has a definition
capture in the repository** — the existing zr-12-10 term captures are floor area, lot area, corner/
interior/through lot, qualifying exterior wall thickness, special density areas, none of which these
texts use). Distinct terms, normalised (F3: de-duplicated to canonical names, no fragments):
bulk; residential buildings; residential; residential equivalent; Residence District; Commercial
District(s); Greater Transit Zone; qualifying residential sites; sky exposure plane buildings; rear
yard; mixed building; yard; story; dwelling units; rooming units; street wall(s); base plane(s);
building(s); building(s) or other structure(s); Manhattan Core; aggregate width of street wall(s);
block; corner lots; lot area; narrow street; wide street(s); outer court; prevailing street wall
frontage; zoning lot(s); qualifying affordable housing; qualifying senior housing. None captured by
this task.

## 8. What was NOT captured, and why

- The 13 pointed-to sections in §7 marked "No" / "No as a unit" — out of this task's named set (34-11,
  34-111, 34-24, 35-53, 35-63 + its children). 23-431/432/433 are already captured.
- **34-112 and 34-113** — they appear in the 34-11 family print/PDF (node 18310) because that node
  prints the 34-1 subtree, but they are NOT in this task's set (the task names 34-11 and 34-111, not
  "every section under 34-11"); not captured.
- All defined terms (§7) — their definitions live in Article I/§12-10; not this task.
- No part of any of the 8 sections was omitted or captured only in part: each section was captured
  WHOLE (every paragraph and list item) and verified word-for-word against its print/PDF. None of these
  sections contains a table or an embedded figure (`saw_table=false`, no `<img>` in any body).

## 9. Checks (each run with its DIRECT exit code; venv `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`)

a. `cd services/api && python -m ruff check .` → "All checks passed!" — **exit 0**
b. `cd services/api && python scripts/sync_zr_snapshots.py --check` → "OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (45 file(s))." — **exit 0**
c. `cd services/api && python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/rules/test_zoning_rule_review_register.py` → "50 passed in 1.06s" — **exit 0**
d. from repo root: `python3 scripts/lanes/check_lane_paths.py --coverage` → "LANE COVERAGE PASS: 8855 file(s), each owned by exactly one lane." — **exit 0**; `python3 tools/modularity_check.py --check` → "selected 715 files; failures 0; warnings 29" (all 29 warnings are pre-existing files I did not touch; no capture file is production source) — **exit 0**
e. `git diff --name-status 8dd39c9f0d2c09bc596063eaf259dc658f29b1c5..HEAD -- docs/research/zr-snapshots/v1` → 8 added (`A`) files only (recorded in the RETURN after the commit)

`test_zr_snapshot_bundle.py` was NOT edited: it discovers captures by directory glob and does not
name individual captures, so it needs no change (allowed-paths condition not triggered). I did NOT run
the full `services/api` pytest suite — the orchestrator runs it once at the wave's final candidate.

## 10. Scope and the no-bend rules

Changes are confined to allowed paths: 8 new canonical capture files under
`docs/research/zr-snapshots/v1/`, their 8 byte-identical synced copies under
`services/api/app/_zr_snapshots/v1/`, and this report. No existing capture, rule file, rule engine,
registry, review register, reference case, plan, helper-research file, other test, dependency file,
`.claude/**`, or any other `project-control/**` file was edited. No new package. No value is shown
anywhere because of a capture. Each capture holds source text only (`extraction_status:
extracted_draft`, `raw_html_verified: false`); nothing here is a Verified zoning determination
(ADR-007: a rule later citing a capture ships under the standing not-professionally-reviewed label with
a direct source link; professional review is advisory).

END-OF-REPORT
