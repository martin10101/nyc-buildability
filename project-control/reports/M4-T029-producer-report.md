# M4-T029 producer report — law-text captures the independent readings named as missing (D-090 R291)

Producer: legal-corpus-engineer (builder), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a7db41cfdff4b8bb7`.
Contract/claim head reset to `cc30ab1884cdb6541c41f0d759ebe198f91a6f46`.
Directive: D-090 R291. This is an AI builder's capture, not a professional or legal review.

Every section and defined term below was read by me NOW from the official NYC DCP Zoning Resolution
portal (`zoningresolution.planning.nyc.gov`), one request at a time, a few seconds apart. For a
SECTION the authoritative, sha256-and-byte-pinned channel is the section's own canonical HTML; its own
print/PDF render was fetched once and used ONLY as a text check (and as the source of the printed
list-item labels). For a ZR 12-10 DEFINED TERM the authoritative channel is the whole §12-10 page HTML
(node 18523, sha256+byte pinned); the whole-page print/PDF (the completeness channel) returned HTTP 504
twice, the documented DB-167 fallback, so the canonical HTML was used. Each capture holds official
**source text only**: no rule, no reading of the text for any lot, no derived number.

26 new canonical files under `docs/research/zr-snapshots/v1/`; 26 byte-identical synced copies under
`services/api/app/_zr_snapshots/v1/` (made by `services/api/scripts/sync_zr_snapshots.py`). No existing
capture was edited. `services/api/tests/rules/test_zr_snapshot_bundle.py` was NOT edited: it discovers
captures by directory glob and names none individually, so the allowed-paths condition for editing it
was not triggered.

## 1. The 16 section captures (one file per section)

`content_digest_sha256` = sha256 of the UTF-8 `verbatim_excerpt`; the runtime loader
(`app/rules/snapshots.py`) recomputes it and fails closed on any mismatch — it loaded all 71 files
clean. HTML channel is `official_channel: html`; `raw_html_sha256` + `response_bytes` are the pinned
provenance. Each section's own print/PDF returned HTTP 200 and its body matched the HTML excerpt
word-for-word (`cross_check.result = match`), EXCEPT the two table sections and the empty-body section,
noted below. Each HTML and each PDF request has its OWN recorded UTC time (F2).

| snapshot_id | § | title (as the page shows it) | node | art/ch | amended | HTML req (UTC) | PDF req (UTC) | HTML bytes | verbatim bytes | content_digest_sha256 |
|---|---|---|---|---|---|---|---|---|---|---|
| zr-23-343 | 23-343 | Rear yard equivalent requirements | 18060 | II/3 | 12/5/2024 | 06:56:03Z | 06:56:07Z | 116886 | 3527 | b4440929d887fa5eba92db8ad881bdf84b04d3283b988026ab58ff6865221680 |
| zr-23-43 | 23-43 | Height and Setback Requirements in R6 Through R12 Districts | 18083 | II/3 | 12/5/2024 | 06:56:11Z | 06:56:19Z | 113353 | 1129 | f5a7cf614d946db4c55bc40168c75f81607707bc087503b22c2343145db41061 |
| zr-23-434 | 23-434 | Height and setback modifications for eligible sites | 18087 | II/3 | 12/5/2024 | 06:56:26Z | 06:56:33Z | 126294 | 3487 | d880eea8c10cb2d2f69e131e7a6f25b5b2abefceba804dbc20f2ebfe4c8e50f9 |
| zr-23-435 | 23-435 | Tower regulations | 18080 | II/3 | 12/5/2024 | 06:56:38Z | 06:56:46Z | 111919 | 487 | a1f5ee7090b0a770ad65e549034b2acd0723f3101b3d2f740a30ab9e20940170 |
| zr-23-436 | 23-436 | Additional height and setback provisions | 18088 | II/3 | 12/5/2024 | 06:56:50Z | 06:56:58Z | 115620 | 2505 | 06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c |
| zr-23-41 | 23-41 | Permitted Obstructions | 18072 | II/3 | 12/5/2024 | 06:57:02Z | 06:57:06Z | 111931 | 377 | edd7781a154c8e47dfd23d27649ba521ed7dabf96ea26c172477d93a29b8a45b |
| zr-23-411 | 23-411 | General permitted obstructions | 22344 | II/3 | 12/5/2024 | 06:57:10Z | 06:57:13Z | 116383 | 4211 | 1c676cfea013722ae606bcf5ee150aed675f6e4a3903c78c2c427c2738e53e9b |
| zr-23-412 | 23-412 | Additional permitted obstructions | 22345 | II/3 | 12/5/2024 | 06:57:18Z | 06:57:26Z | 115618 | 3053 | 879668ea1c3f2d4fa9a1c6976d5b807c59e7f37849b92afe29bc6205eb8183f7 |
| zr-23-413 | 23-413 | Permitted obstructions in certain districts | 18073 | II/3 | 12/5/2024 | 06:57:30Z | 06:57:37Z | 114503 | 2356 | bd2431480480c84f29cdfa93ef0f38eecfb83f07c1187908b17c409af604978f |
| zr-34-112 | 34-112 | Residential bulk regulations in other C1 or C2 Districts or in C3, C4, C5 or C6 Districts | 18312 | III/4 | 12/5/2024 | 06:57:42Z | 06:57:47Z | 97134 | 373 | 19e8c488831398c112a19306b72f6112454cf42ec184cc05f2f1235dc36c857f |
| zr-34-113 | 34-113 | Existing public amenities for which floor area bonuses have been received | 18313 | III/4 | 10/17/2007 | 06:57:51Z | 06:57:57Z | 76397 | 1672 | 17535e8a19f5b210bf9106af3f98aae794174ab5860c07a7f9ac17bfc4c114ad |
| zr-34-21 | 34-21 | General Provisions | 18315 | III/4 | 12/5/2024 | 06:58:01Z | 06:58:06Z | 74524 | 512 | 6da11080e5d4012f0f9e771595e3e9434a8cafc6fdd5aa02f517d33d929e09b8 |
| zr-35-62 | 35-62 | Height and Setback Requirements in Commercial Districts With R1 Through R5 Equivalency | 18287 | III/5 | 12/5/2024 | 06:58:11Z | 06:58:17Z | 87630 | 1865 | 2d5b82e080118005897e7419b4bcd042cbccdc686d6dd0d646f7c813f6d63848 |
| zr-35-64 | 35-64 | Special Provisions for Certain Areas | 22822 | III/5 | 12/5/2024 | 06:58:21Z | 06:58:27Z | 84599 | 42 | 5baf8c24274f58277c3bca6522e234eb11f546e7a24ee0c19614a9e234fac328 |
| zr-35-71 | 35-71 | Planting | 22961 | III/5 | 12/31/1969 | 06:58:32Z | 06:58:35Z | 84740 | 335 | e5086a5e86a8ea45e990fc3f3ad30d2ec324ae7b4512cfc2ed01bff82910ba1c |
| zr-36-64 | 36-64 | Special Provisions for Zoning Lots Divided by District Boundaries | 17978 | III/6 | 6/6/2024 | 06:58:39Z | 06:58:46Z | 103528 | 334 | 79fadf89852febb0486d74221c7ba8297edc734c8becce2a112ddadc1c47a8be |

The `raw_html_sha256` for each is pinned in the capture's `source` block (first 12 chars, in order:
4ed87d9512a6, eab4a77a846f, 93c5d7648a21, 1b1eccb18d66, 5d18071d3d4e, cb199aa188ce, b2adadc9e165,
bbd10ddac1a5, 92a0dd7ffb3b, 34026553b27f, 19da2b394d41, 9c239c6f9bd1, 74c1d56d4c29, 33ac0bb32d8c,
396bc0f3da08, 6de53d45905e). Each page carries exactly one per-section machine-readable
`<time datetime>` stamp keyed to its `data-section-number`, EXCEPT 35-71 (see §4). The print/PDF bytes
are NOT pinned (F4): the portal regenerates the PDF per request with the day's date embedded; the
observed bytes/sha256 are recorded only under `cross_check.observed_*_nonreproducible`.

## 2. The 10 ZR 12-10 defined-term captures (one file per term)

All ten were extracted from the SAME one whole-§12-10-page HTML fetch (node 18523, HTTP 200,
response_bytes 1,316,758, raw_html_sha256 `3c7197026d616c459fd38b3cc76ccc607b7891f600e5a1ec00053ceb8574b5bc`,
retrieved 2026-10-07T07:10:58Z). The whole-page print/PDF (entityprint/pdf/node/18523) was attempted at
07:11:02Z (HTTP 504) and retried at 07:12:26Z (HTTP 504, ~59 s) — the documented DB-167 behaviour — so
the canonical HTML is the channel (`cross_check.result = unavailable_documented_fallback`). Each term's
per-term Last Amended stamp and node id are its own.

| snapshot_id | defined term | term node | amended | verbatim bytes | content_digest_sha256 |
|---|---|---|---|---|---|
| zr-12-10-lot-line-front | lot line, front | 21599 | 12/15/1961 | 38 | 6bd9212cbb4ffb4671c692c92f6b265a1ab60e114778925048bc66b3a6cdbbbc |
| zr-12-10-lot-line-rear | lot line, rear | 21600 | 12/15/1961 | 211 | d34da91dcfa8392e655806a06204621c80175de99a034d983b978cb73e45c86b |
| zr-12-10-lot-line-side | lot line, side | 21601 | 12/15/1961 | 89 | 5ba11f6adfc47e15f68c20ca93e4dc5e053458725796eb74c8deb0ced8c67221 |
| zr-12-10-lot-width | lot width | 21603 | 12/15/1961 | 91 | 35e17792ba3b7333edde3cc195c7f5fa4851398404b104c4c3cd766092c10f25 |
| zr-12-10-lot-depth | lot depth | 21596 | 12/15/1961 | 286 | 442b1fbe2814c50a6c5142ccaf08d9293f52bbd63390170178c2b0b91fb6d711 |
| zr-12-10-zoning-lot | zoning lot | 21709 | 2/2/2011 | 8145 | 0547550b1bcc8c5b8e5ff5fa3f429e139cd2a95bf4a7270a85fc4cd8cce9d53a |
| zr-12-10-street-line | street line | 21677 | 10/25/1973 | 199 | 20495a0325bef1576623272bd4c4628ce994edf9decd7da3214a7f3708b65a5f |
| zr-12-10-manhattan-core | Manhattan Core | 21607 | (none shown) | 96 | 2c04132a96a435146c01f3c0a0578ea26520b10c2c5d1a894470ba8a47c59c56 |
| zr-12-10-base-plane | base plane | 21517 | 5/12/2021 | 3226 | f57cd9b62e591236908fe65163f7162605e03ca8604c5c4e6fe4e48a4f56eae2 |
| zr-12-10-special-downtown-brooklyn-district | Special Downtown Brooklyn District | 21721 | 2/2/2011 | 172 | ae66c93e8ec466de81587358a332c40c15fd500fc4f34ae4102c11ab43d7dd2d |

**NONE of the ten term definitions contains an ordered list (no `<ol>` in any).** So there are NO
list-position labels in any term capture; any parenthesised `(a)/(b)/(1)` in a definition (e.g. "zoning
lot" (a)-(f), "base plane" (a)-(c)) is LITERAL text of the official definition, not a label added by
the capture. The DB-167 F1 gap (whole-page PDF 504 means list-marker glyphs are unconfirmable) therefore
does not affect any text captured here; each file's notes state this. The §12-10 page header (node
18523, title "DEFINITIONS") shows Last Amended 3/26/2026 (read first-hand), which is the date of the
most-recently-amended term on the page; each capture records its own per-term stamp as the operative
provenance.

## 3. Sections found under 23-41 and under 35-71

- **Under 23-41 (Permitted Obstructions):** the 23-41 family print/PDF (node 18072) renders exactly
  **23-411** (General permitted obstructions), **23-412** (Additional permitted obstructions), and
  **23-413** (Permitted obstructions in certain districts). No 23-414 or any further 23-41x exists on
  the page. All three are captured.
- **Under 35-71:** **NONE.** The 35-71 family print/PDF (node 22961) renders ONLY 35-71 itself. 35-71
  has no sections numbered under it. (This is tied to §4.)

## 4. A visible conflict in the live Resolution — 35-71 (recorded, not resolved)

The task named 35-71 because the captured ZR 34-24(b)(3) points to it: "where the optional #bulk#
regulations for #sky exposure plane buildings# are utilized, the provisions set forth in Section 35-71,
inclusive, shall be applied." **But the live ZR 35-71 page (node 22961) is titled "Planting"**, and its
entire body is: "The provisions of Section 23-613 (Front yard planting requirements) shall apply, except
that plantings shall additionally not be required in the area of the #zoning lot# between the #street
line# and any portion of #ground floor level# #street walls# allocated to non-residential #uses# with no
sleeping accommodations." It has no subsections. I captured 35-71 exactly as the official page shows it
and did NOT substitute any "sky exposure plane" section (that would be a guess). I surface the conflict
here for a rules task to resolve; I did not change any rule file, and I did not search for or capture a
different section in its place. Also, 35-71's page carries NO machine-readable `<time datetime>` stamp;
its `.amended` field shows the literal "12/31/1969" (the Unix-epoch date, i.e. the portal records no real
amendment date for this section). The capture records this verbatim and `last_amended_machine_readable`
is null, stated as observed.

## 5. 35-64 has no operative body text of its own

ZR 35-64 "Special Provisions for Certain Areas" (node 22822) is a heading/container only: the official
page's section-body container (`div.sec-body`) is EMPTY. Its print/PDF renders the heading and its Last
Amended stamp, then the subsections **35-641, 35-642, 35-643**. The capture's `verbatim_excerpt` is the
displayed section number and title only, and its notes state the empty body plainly. The task named
"ZR 35-64" (its own text), not its subsections (the "and every section numbered under it" phrase binds to
35-71), so 35-641/35-642/35-643 are listed here as pointed-to, not captured.

## 6. The two tables (23-434 and 34-112) — captured cell by cell

Both sections contain an HTML `<table>`. Following the accepted precedent of the committed zr-23-432
capture, each table is NOT inlined as prose: its place in `verbatim_excerpt` is marked
`[table - see structured `table` field]`, and the table is carried cell-by-cell in a top-level `table`
field (`columns`, then one row object per table row with `cells` in left-to-right order and a per-cell
`cell_footnotes` marker). The composition note in each file says how.

- **23-434** table "MAXIMUM BUILDING HEIGHT FOR ELIGIBLE SITES": columns `District` and
  `Maximum height of #buildings or other structures# (in feet)`; 11 rows (R6-2→95; R6 R6-1→125;
  R7-1 R7-2→155; R7-3→185; R8→215; **R8 with footnote marker 1→255**; R9→285; R9-1→315; R10→355;
  R11→405; R12→495). The `R8`+superscript-`1` row is recorded as district `R8` with `cell_footnotes`
  `"1"` (NOT the ambiguous "R81" the PDF/HTML-flattening would show); footnote 1 ("for #UAP
  developments# or #qualifying senior housing# on #zoning lots#, or portions thereof, within 100 feet of
  a #wide street#") is in both the excerpt and a `footnotes` field. The rest of 23-434 (paragraphs
  (a)/(b) with the (1)/(2)/(i)-(v)/(3)/(i)-(ii) list) matched the print/PDF word-for-word.
- **34-112** table (district → residential equivalent): columns `Districts` and
  `Applicable #residential equivalent#`; 20 rows (C3→R3-2 … C4-12 C6-12→R12), read directly from the
  unambiguous HTML `<table>` cells. NOTE: `pdftotext -layout` renders the two-column table so the long
  district cells wrap and interleave across the two columns (e.g. the R10 row prints "C6- R10 7" where
  the HTML cell is "C1-9 C2-8 C4-6 C4-7 C5 C6-4 C6-5 C6-6 C6-7 C6-8 C6-9"); the HTML cell order is
  authoritative and is what the `table` field records. The print/PDF confirms each row's
  district→equivalent mapping and the token set; only the visual left-to-right order of the long cells
  is a `-layout` artifact. This is disclosed in the capture's `cross_check.method`.

## 7. What was NOT captured, and why

- **"residential" — NOT captured: ZR 12-10 does not define it as a standalone term.** The §12-10 page
  (node 18523) has 446 defined-term articles; there is no `id="term-residential"`. The related terms
  that DO exist as separate §12-10 definitions are: `residential building`, `residential equivalent`,
  `residential plaza`, `residential street`, `residential use`. The task listed "residential" as a term
  to capture "if ZR 12-10 defines it" (the explicit caveat the task attached to Special Downtown Brooklyn
  District applies equally here per RULES: never guess); it does not define "residential" on its own, so
  nothing is captured for it and nothing is filled from a guess. If the amenity-allowance base "residential
  floor area" (measurement-basis gap) needs a defined base, that base is not a standalone §12-10 term and
  remains an open gap for a rules/measurement task — not resolvable from a capture.
- **35-641/35-642/35-643** — subsections of 35-64, outside this task's named set (§5); listed, not captured.
- The pointed-to sections in §8 marked "No" — outside this task's named set; listed, not captured.

Everything else named by the task is captured. "Special Downtown Brooklyn District" IS a §12-10 term
(node 21721) and is captured; its definition names the district and points to Article X, Chapter 1 for
the special regulations themselves (the definition text is what is captured here).

## 8. Every further section / defined term the new texts point to (LISTED, not captured)

Sections referenced by the new texts, with pointing words (≤25) and whether the repository already holds
a capture (checked against all 71 snapshots now in the store):

| section | pointed-to from | pointing words | already captured? |
|---|---|---|---|
| 23-34 (incl.) | 23-343 | "except as otherwise provided pursuant to the provisions of Section 23-34, inclusive" | No |
| 23-341 | 23-343 | "except as provided in Section 23-341 (Permitted obstructions in required yards or rear yard equivalents)" | No |
| 23-311 / 23-312 | 23-343 | "obstructions in any yard or rear yard equivalent set forth in Sections 23-311 and 23-312 shall be permitted" | No |
| 23-431 | 23-43, 23-436, (34-112 via equiv.) | "street wall location regulations of Section 23-431" | Yes (zr-23-431) |
| 23-432 | 23-43, 23-435, 23-436 | "height and setback requirements of Section 23-432" / table rows | Yes (zr-23-432) |
| 23-433 | 23-43, 23-436 | "setback regulations of Section 23-433" | Yes (zr-23-433) |
| 23-44 (incl.) | 23-43 | "additional height and setback provisions are set forth in Section 23-436 and Section 23-44, inclusive" | No |
| 23-42 | 23-41, 35-62 | "the applicable yard regulations of Section 23-42" | Yes (zr-23-42) |
| 23-421 / 23-423 / 23-424 | 23-413, 35-62 | "yard regulations ... Sections 23-421 ... 23-423 ... 23-424" | Yes (zr-23-421/423/424) |
| 23-62 | 23-412 | "Balconies, unenclosed, subject to the provisions of Section 23-62 (Balconies)" | No |
| 26-50 | 23-412 | "equipment shall be subject to the applicable provisions of Section 26-50 (Special Screening and Enclosure Provisions)" | No |
| 23-613 | 35-71 | "The provisions of Section 23-613 (Front yard planting requirements) shall apply" | No |
| 34-11 | 34-21 | "regulations ... made applicable ... in Section 34-11 (General Provisions)" | Yes (zr-34-11) |
| 34-22 | 34-21 | "modified by the provisions of Sections 34-22 (Modification of Floor Area Regulations), 34-23, 34-24" | No (34-24 is captured) |
| 35-22 | 35-62 | "as modified by the provisions of Section 35-22 (Residential Bulk Regulations in C1 or C2 Districts ...)" | No |
| 35-641 / 35-642 / 35-643 | 35-64 | subsections the 35-64 family print renders (35-64 has no own body) | No |
| 37-727 / 37-73 | 34-113 | "floor area bonus ... pursuant to Section 37-727 (Hours of access)" / "Section 37-73 (Kiosks and Open Air Cafes)" | No |
| 74-761 | 34-113 | "by special permit of the City Planning Commission, pursuant to Section 74-761 (Elimination or reduction ...)" | No |
| 23-435 / 23-436 / 23-441 | 35-633, 35-64 family, 35-632 | tower / additional provisions cross-refs | 23-435, 23-436 captured here; 23-441 No |

Defined terms the new texts use are all Article I / §12-10 terms. Of them, these now HAVE a §12-10
capture in the repository (6 captured earlier or by this task): `base plane`, `floor area`, `lot area`,
`qualifying exterior wall thickness`, `street line`, `zoning lot` — plus the ten captured by this task
(§2). The many other defined terms used (e.g. `residential equivalent`, `Commercial District`,
`narrow street`, `wide street`, `rear yard`, `curb level`, `street wall line level`, `building segment`,
`ground floor level`, `UAP development`, `qualifying senior housing`, `front lot line`, `corner lot`,
`through lot`, `interior lot`, `side lot line`, `lot coverage`, `non-complying building`, etc.) are
§12-10 defined terms NOT in this task's named set and are not captured here.

Plain-text references (not section numbers), pointed to, not captured as units: "Article II, Chapter 3",
"Article III, Chapter 4", "Article III, Chapter 6", "Article X, Chapter 1" (Special Downtown Brooklyn),
"the New York City Building Code", "the New York City Fire Code", "the New York City Administrative Code".

## 9. Checks (each run with its DIRECT exit code; venv `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`)

a. `cd services/api && python -m ruff check .` → "All checks passed!" — **exit 0**
b. `cd services/api && python scripts/sync_zr_snapshots.py --check` → "OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (71 file(s))." — **exit 0** (run after `sync_zr_snapshots.py` write, which synced the 26 new copies)
c. `cd services/api && python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py tests/rules/test_zoning_rule_review_register.py` → "50 passed in 1.04s" — **exit 0**
d. from repo root: `python3 scripts/lanes/check_lane_paths.py --coverage` → "LANE COVERAGE PASS: 8920 file(s), each owned by exactly one lane." — **exit 0**; `python3 tools/modularity_check.py --check` → "selected 716 files; failures 0; warnings 29" (all 29 warnings are pre-existing production files I did not touch; no capture file is handwritten production source) — **exit 0**
e. `git diff --name-status cc30ab18..HEAD -- docs/research/zr-snapshots/v1` → 26 added (`A`) files only (captured in the RETURN after the commit)

I did NOT run the full `services/api` pytest suite — the orchestrator runs it once at the wave's final
candidate. The method was validated before capturing: my programmatic extractor reproduces the accepted
committed capture `zr-35-631` byte-for-byte (content_digest 816bc747…) and the committed §12-10 term
captures (`lot, corner`, `lot, interior`, `lot, through`, `lot area` byte-for-byte; `floor area`
word-for-word, 1414 words), from the same official pages read now.

## 10. Scope and the no-bend rules

Changes are confined to allowed paths: 26 new canonical capture files under
`docs/research/zr-snapshots/v1/`, their 26 byte-identical synced copies under
`services/api/app/_zr_snapshots/v1/`, and this report. No existing capture, rule file, rule engine,
registry, review register, reference case, plan, helper-research file, other test, dependency file,
`.claude/**`, or any other `project-control/**` file was edited. No new package. No value is shown
anywhere because of a capture. Each capture holds source text only (`extraction_status:
extracted_draft`, `raw_html_verified: false`); nothing here is a Verified zoning determination (ADR-007:
a rule later citing a capture ships under the standing not-professionally-reviewed label with a direct
source link; professional review is advisory).

END-OF-REPORT
