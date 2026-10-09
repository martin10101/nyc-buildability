# M4-T033 producer report — further law-text captures named by the step-P4 readers (D-090 R291)

Producer: legal-corpus-engineer (builder), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-aa29d217ad1d0cb21`.
Contract/claim head reset to `6979d27d96068de2130d2624854cf125117d6032`.
Directive: D-090 R291. This is an AI builder's capture, not a professional or legal review.
Source text only: no rule, no reading of any text for any lot, no reference case / register / result changed.

Every target below was read by me NOW (2026-10-07) from the official NYC DCP Zoning Resolution portal
(`zoningresolution.planning.nyc.gov`), one request per page, a few seconds apart. Channels follow the
accepted M4-T031 method: for a SECTION the authoritative, sha256-and-byte-pinned channel is the section's
own canonical HTML (`field--name-body`); its own print/PDF (HTTP 200) is a text check and the source of
confirmed list labels. For a ZR 12-10 DEFINED TERM the authoritative channel is the whole §12-10 page HTML
(node 18523, sha256 and byte count pinned; byte-identical to M4-T031's pinned page); the whole-page
print/PDF completeness channel returns HTTP 504 (the documented DB-167 fallback), so list-item labels in a
term are markup positions, disclosed as such.

**Extractor validated before capturing** (the M4-T029/M4-T031 practice): my programmatic term extractor
reproduces the committed `zr-12-10-lot-coverage`, `-curb-level`, `-mixed-building`, `-street-wall`,
`-dwelling-unit` and the 3-level-list `zr-12-10-qualifying-residential-site` **byte-for-byte** (content
digest match); my section extractor reproduces the committed `zr-34-232` and the list-heavy `zr-23-341`
byte-for-byte. End-to-end, all 22 new section/term captures re-extract identically from the pinned source
and every recorded `raw_html_sha256`/`response_bytes` matches.

## 23 new captures (one file per target) + 23 byte-identical synced copies

New canonical files under `docs/research/zr-snapshots/v1/`; synced copies under
`services/api/app/_zr_snapshots/v1/` by `scripts/sync_zr_snapshots.py`. No existing capture edited or
re-fetched in place. `tests/rules/test_zr_snapshot_bundle.py` NOT edited (it discovers by directory glob
and names no id). IDs:

- Terms (13): `zr-12-10-floor-area-ratio`, `-limited-height-district`, `-aggregate-width-of-street-walls`,
  `-block`, `-short-dimension-of-a-block`, `-transportation-infrastructure-adjacent-frontage`,
  `-transit-zone-greater`, `-transit-zone-outer`, `-multiple-dwelling-residence`, `-height-factor`,
  `-open-space`, `-open-space-ratio`, `-public-park`.
- Sections (9): `zr-23-322`, `zr-23-335`, `zr-23-381`, `zr-23-62`, `zr-23-20`, `zr-35-00`, `zr-35-01`,
  `zr-35-20`, `zr-35-21`.
- 34-23 sub-section list (1): `zr-34-23-contents`.

## Per target group — found/not, with the number and title the SITE shows

**(1) ZR 12-10 definition of "floor area ratio" — FOUND.** Exact-title defined-term article `floor area
ratio` (/node/21559, Last Amended 2/2/2011). Captured `zr-12-10-floor-area-ratio`. Searched exact
("floor area ratio"), inverted, and combined titles; it is its own exact-title article (distinct from
"floor area", /node/21558, already captured). No ordered list; its one example is literal text.

**(2) Front and side yard REQUIREMENTS for residences in R6–R12 — FOUND, two sections.** Under 23-32
(Front Yard Requirements) the site shows **23-322 "Front yard requirements for R6 through R12 Districts"**
(/node/22758); its body: "In the districts indicated [R6 R7 R8 R9 R10 R11 R12], no #front yard#
requirements shall apply." Under 23-33 (Side Yard Requirements) the site shows **23-335 "Side yard
requirements for R6 through R12 Districts"** (/node/18048); its body has (a) Detached buildings (two 5-ft
side yards for single-/two-family detached residences) and (b) All other buildings (no side yards
required; a provided side open area must be ≥5 ft). Captured `zr-23-322`, `zr-23-335`. (These are the
R6–R12 siblings of the R1–R5 sections 23-321/23-332; the headers 23-32/23-33 are grouping titles only.)

**(3) Section ZR 23-443(a) points to for zoning lots adjoining public parks — FOUND: 23-381.** The site
shows **23-381 "Special provisions in other geographies"** (/node/22766, under 23-38 Special Rules for
Certain Areas). Its body governs buildings containing multiple dwelling residences on zoning lots that
adjoin a public park (the light-and-air / legally-required-window provision). Captured `zr-23-381`.

**(4) Section on balconies that ZR 23-341 and ZR 23-312 point to — FOUND: 23-62.** The site shows
**23-62 "Balconies"** (/node/18007, under 23-60 Additional Design Elements). Captured `zr-23-62`
(districts R1–R12; nested list (a)/(1)/(2)/(3), (b)/(1)/(i)/(ii)/(iii), (2) — labels confirmed EQUAL to
its print/PDF).

**(5) Twelve ZR 12-10 definitions — ALL FOUND (each searched exact / inverted / combined).**
- `Limited Height District` /node/21588 (12/5/2024) — exact title; refs 23-443, 24-591, 33-491.
- `aggregate width of street walls` /node/21510 (2/2/2011) — exact title; body + an omitted embedded
  diagram whose all-caps caption "AGGREGATE WIDTH OF STREET WALLS" is retained (disclosed).
- `block` /node/21519 (12/15/1961) — exact title; literal (a)–(f) list in `<p>` text (no `<ol>`).
- `short dimension of a block` /node/22728 (12/5/2024) — exact title (defined IN §12-10, one sentence:
  a block frontage where the dimension between two bounding streets is < 230 feet).
- `transportation-infrastructure-adjacent frontage` /node/22738 (12/5/2024) — exact title; ordered list
  (a)–(d) → markup positions (both PDF channels unavailable; see below).
- `Greater Transit Zone` is a CROSS-REFERENCE (/node/22734 = "see #Transit Zone, Greater#"); operative
  definition captured from the inverted-title article **`Transit Zone, Greater`** /node/22733 (12/5/2024)
  as `zr-12-10-transit-zone-greater` (literal (a)/(b)/(c) in `<p>`; no `<ol>`).
- `Outer Transit Zone` is a CROSS-REFERENCE (/node/22737 = "see #Transit Zone, Outer#"); operative
  definition captured from **`Transit Zone, Outer`** /node/22736 (12/5/2024) as
  `zr-12-10-transit-zone-outer` (ordered list (a)/(b) → (1)/(2); markup positions).
- `multiple dwelling residence` /node/22719 (12/5/2024) — exact title (singular article; the texts use
  "#multiple dwelling residences#", the plural of this same term).
- `height factor` /node/21567 (3/22/2016) — exact title.
- `open space` /node/21618 (7/8/2025) — exact title (distinct from "open space ratio", "designated
  open space", "open space network"); has literal (a)–(c) then (1)–(4) list in `<p>` text (no `<ol>`).
- `open space ratio` /node/21619 (2/2/2011) — exact title.
- `public park` /node/21630 (12/15/1961) — exact title (distinct from "public parking garage/lot").

**(6) Opening sections of Article III, Chapter 5 stating applicability — FOUND, four sections.**
- **35-00 "APPLICABILITY"** /node/18255 — header only (empty `div.sec-body`); its print/PDF renders the
  subtree 35-01…35-04. Captured header-only `zr-35-00` (`no_own_body`).
- **35-01 "Applicability of This Chapter"** /node/18256 (12/5/2024) — operative: the Chapter's bulk
  regulations apply to any mixed building in a Commercial District, and to multi-building zoning lots with
  residential + commercial/community-facility uses, and where incorporated by cross-reference. Captured
  `zr-35-01`.
- **35-20 "APPLICABILITY OF RESIDENCE DISTRICT BULK REGULATIONS"** /node/18261 (2/2/2011) — header only.
  Captured header-only `zr-35-20` (`no_own_body`); subtree 35-21…35-24.
- **35-21 "General Provisions"** /node/18262 (2/2/2011) — operative: in C1–C6, the Article II Ch 3 bulk
  regulations apply to all residential portions of buildings as modified by the remaining Chapter-5
  sections. Captured `zr-35-21`. (35-22 is already captured; not re-fetched.) These four, with 35-22,
  are the texts the readers said they needed to decide whether 35-22 or 34-111 governs; I draw no
  conclusion — source text only.

**(7) The page of ZR 34-23 and its sub-sections — CAPTURED as a separate file `zr-34-23-contents`.** The
official Article III, Chapter 4 contents navigation (request `/article-iii/chapter-4`, sha256 and bytes
pinned) shows section 34-23 "Modification of Yard and Open Area Regulations" with **EXACTLY THREE child
sub-sections: 34-231 (Modification of front yard requirements), 34-232 (Modification of side yard
requirements), 34-233 (Change of use)**. **No child exists beyond 34-233** — the next contents entry,
34-24 "Modification of Height and Setback Regulations", is a SIBLING of 34-23 (outside its
`data-children-for="34-23"` container). Corroborated by the 34-23 section print/PDF (node 18322, HTTP 200)
which renders the subtree 34-23 + 34-231 + 34-232 + 34-233 and nothing more. The existing capture
`zr-34-23` (the 34-23 page's own, EMPTY body) is NOT edited; this is a separate added file, as instructed.

**(8) ZR 23-20 and its opening text — FOUND, a page of its own exists.** The site shows **23-20 "FLOOR
AREA REGULATIONS"** (/node/18024, 12/5/2024) with its OWN body text (not a bare header): it routes floor
area to 23-21 (R1–R5), 23-22 (R6–R12), 23-23 (multiple dwelling residences), 23-24 (certain areas), and
states the rule for zoning lots with multiple uses/buildings subject to different floor area ratios.
Captured `zr-23-20` (the 23-20 page's own body only; its print/PDF prints the whole 23-2x subtree).

## Channels that did not answer
- The §12-10 whole-page print/PDF (`entityprint/pdf/node/18523`) returned **HTTP 504** (41-byte timeout
  body), retried once with the same result — the documented DB-167 fallback. All 13 term captures record
  this and use the sha256-pinned canonical §12-10 HTML.
- The per-term print/PDF for the two list-bearing terms returned **HTTP 403** (57,524-byte error page):
  node 22738 (transportation-infrastructure-adjacent frontage) and node 22736 (Transit Zone, Outer). So
  there is NO glyph-authoritative channel for those two terms' ordered-list labels; their labels are
  recorded as markup positions (HTML ordered-list nesting; the ZR §12-10 (a)/(1)/(i) scheme that
  reproduces the accepted `zr-12-10-qualifying-residential-site`), disclosed as DB-167 F1, and their items
  should be cited by words. All nine SECTION print/PDFs returned HTTP 200; their list labels are confirmed
  EQUAL to the print/PDF (e.g. 23-62: (a),(1),(2),(3),(b),(1),(i),(ii),(iii),(2)).

## Further sections / terms the new texts point to that are NOT captured (listed, not captured)
23-443, 24-591, 33-491 (from Limited Height District); 66-11 Definitions (from Transit Zone, Outer);
24-181, 35-712 (from open space); 23-21/23-22/23-23/23-24 and "Article II, Chapter 3" (from 23-20 and
35-21); 23-62 is now captured (was pointed-to by 23-341/23-312); 23-381 is now captured (pointed-to by
23-443(a)); further §12-10 terms used but outside this task's named set (e.g. #special parking areas#,
#Inner Transit Zone#, #select mass transit stations#, #legally required window#, #community facility
building#, #non-residential building#). None is captured beyond this task's named set.

## Checks — each with its DIRECT exit code
Run with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest
`-p no:cacheprovider`; checks a–c from `services/api`, check d from repo root. Exit code read directly
(`$?` / `${PIPESTATUS[0]}`), not through a pipe.
- a. `python -m ruff check .` → "All checks passed!" — **exit 0**
- b. `python scripts/sync_zr_snapshots.py --check` → "OK: runtime-bundled ZR snapshots are byte-identical
  to the canonical source (133 file(s))." — **exit 0** (110 prior + 23 new)
- c. `python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py
  tests/rules/test_zoning_rule_review_register.py` → "50 passed" — **exit 0** (the default-store load
  recomputed all 133 content digests clean and verified byte-identity/membership)
- d. from repo root: `python3 scripts/lanes/check_lane_paths.py --coverage` → "LANE COVERAGE PASS: 9185
  file(s), each owned by exactly one lane." — **exit 0**
- e. `git status --porcelain` → clean after commit; `git diff --name-status 6979d27d…HEAD` =
  **46 added (`A`)** (23 under `docs/research/zr-snapshots/v1/` + 23 under
  `services/api/app/_zr_snapshots/v1/`) + **1 modified (`M`)** = this report
  (`project-control/reports/M4-T033-producer-report.md`, a pre-seeded placeholder at the contract head,
  now filled in — an allowed path). No existing capture, and no file outside allowed paths, modified or
  deleted; the bundle test is NOT edited. I did NOT run the full `services/api` pytest suite (the
  orchestrator runs it once at the wave's final candidate).

## Scope and the no-bend rules
Changes confined to allowed paths: 23 new canonical captures, their 23 byte-identical synced copies, and
this report. No existing capture, rule, rule engine, registry, review register, reference case, plan,
other test, dependency file, `.claude/**`, or any other `project-control/**` file edited. No new package.
Each capture holds source text only (`extraction_status: extracted_draft`, `raw_html_verified: false`);
nothing here is a Verified zoning determination (ADR-007).

## Doubt / limitations disclosed
1. The two list-bearing TERMS (`transportation-infrastructure-adjacent-frontage`, `transit-zone-outer`)
   carry markup-position list labels, NOT confirmed printed glyphs, because both §12-10 PDF channels are
   unavailable (whole-page 504, per-term 403; DB-167 F1). The item TEXT is verbatim from the sha256-pinned
   canonical HTML; cite items by their words. SECTION list labels are confirmed against the print/PDF.
2. `zr-12-10-aggregate-width-of-street-walls` omits an embedded diagram image and retains its all-caps
   caption line as official page text (disclosed in the capture).
3. The `zr-34-23-contents` capture pins the Article III Chapter 4 contents HTML and is corroborated by the
   34-23 print/PDF subtree; it is a sub-section list, not a reading.
4. No capture has been independently re-read by a second agent (`raw_html_verified: false`); the
   independent reading of these texts is a later task. None of these texts has been interpreted for any lot.

Round 2: the amendment date of `open space` corrected from 12/15/1961 to 7/8/2025 (review finding F1); every date and node in this report compared with the capture files.

END-OF-REPORT
