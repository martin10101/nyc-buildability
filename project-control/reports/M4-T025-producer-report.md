# M4-T025 producer report — law-text captures for the R6B checks and the measurement basis (step P1)

Producer: legal-corpus-engineer (build). Role: write files + one commit in an isolated worktree; no
review, no accept, no push, no ledger. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a0e30f78add0c5dac`.
Claim-seam head reset to: `f21ea5bbac8ce1f95115eba9f2398dd2a2c18229`.
Directive refs: D-090 R400 (Section 23-23 recorded as law only from captured official text), R403
(Section 12-10 exclusions checked against the text). Discovery: DB-156.

All text was read by me from the official DCP Zoning Resolution portal
(`zoningresolution.planning.nyc.gov`) during this session on 2026-10-07 via direct HTTPS GET
(`curl -A Mozilla/5.0`), the method the accepted captures use. Each capture pins the exact bytes it was
drawn from by sha256. The helper reading of 2026-10-06 (RQ006/007/008) was used only as a lead for
addresses and node ids; no capture text came from it.

## What was captured (14 new capture files; one per section and one per 12-10 defined term)

ID pattern follows the repo: `zr-<section>` for a section, `zr-12-10-<term>` for a 12-10 defined term
(each 12-10 term is a distinct portal node with its own Last Amended date, so each gets its own file).
Nothing was shown/derived anywhere from a capture; no rule, register, reference case, plan, screen or
other test changed.

### Group A — ZR 12-10 defined terms (completeness channel print/PDF node 18523 = HTTP 504, documented fallback to canonical HTML)

Shared HTML channel for all seven: `https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10`
(whole §12-10 page, portal node 18523), HTTP 200, response_bytes 1316758,
raw_html_sha256 `3c7197026d616c459fd38b3cc76ccc607b7891f600e5a1ec00053ceb8574b5bc`, read 2026-10-07.
Completeness/cross-check channel attempted for each: `entityprint/pdf/node/18523` → 302 →
`print/pdf/node/18523` → HTTP 504 (Gateway Timeout), retried once (~59 s, 504 again) — the same behaviour
the accepted `zr-12-10` capture documents. Per that documented fallback the canonical HTML channel was
used; the §12-10 print/PDF could not confirm list-marker glyphs. The per-term node page and its
print/PDF both return HTTP 403, so the term text is served only inside the whole-page HTML.

| snapshot_id | defined term (node) | last amended | excerpt bytes | content_digest_sha256 |
|---|---|---|---|---|
| zr-12-10-lot-corner | "lot, corner" (21594) | 1965-05-20 (5/20/1965) | 946 | 86b686b683e4… |
| zr-12-10-lot-interior | "lot, interior" (21597) | 1961-12-15 (12/15/1961) | 81 | 6897ea4af3af… |
| zr-12-10-lot-through | "lot, through" (21602) | 1961-12-15 (12/15/1961) | 398 | d71f24ad1ff0… |
| zr-12-10-lot-area | "lot area" (21591) | 1964-02-20 (2/20/1964) | 41 | 5fe518c6a26a… |
| zr-12-10-special-density-areas | "special density areas" (22730) | 2024-12-05 (12/5/2024) | 269 | e8029ab3bcc6… |
| zr-12-10-floor-area | "floor area" (21558) | 2024-12-05 (12/5/2024) | 8884 | e14ecafcb5f2… |
| zr-12-10-qualifying-exterior-wall-thickness | "qualifying exterior wall thickness" (22339) | 2023-12-06 (12/6/2023) | 1387 | 119324c8b823… |

Notes on Group A:
- The alphabetical terms "corner lot" (node 21535), "interior lot" (21580) and "through lot" (21686)
  are cross-references ("see lot, corner" / "…interior" / "…through"); the operative definitions are the
  "lot, corner/interior/through" terms, which is what is captured. Each cross-reference is recorded in
  the capture's notes.
- "special density areas" — the official term is plural; its "(a)/(b)" are LITERAL text of the
  definition (`<p>` text on the page), not labels added by me.
- "floor area" — captured IN FULL: the opening, the 12-item "includes" list (with item 11's three
  nested criteria) and the 17-item "shall not include" list (with nested parking, balcony/terrace and
  stairwell sub-items). Because the §12-10 print/PDF is unavailable, ordered-list items carry a
  parenthesized label that is the item's ORDINAL POSITION in its HTML ordered list, one distinct family
  per nesting depth (depth 1 arabic (1); depth 2 lowercase roman (i); depth 3 lowercase letter (a);
  depth 4 uppercase letter (A)) so nesting is never ambiguous. These labels are a markup-position
  representation, NOT a transcription of a confirmed glyph; the item TEXT is verbatim from the pinned
  HTML. The HTML nests the "shall not include" list inside the markup of includes-item (12); it is
  represented as the separate list its introducing sentence establishes, numbered afresh (disclosed in
  the composition note; no text changed).
- The floor-area capture also LISTS (does not capture) the other ZR 12-10 defined terms its exclusion
  items name (R403): 'cellar'/'Cellar', 'accessory', 'story', 'single-', 'two-family residence',
  'zoning lot(s)', 'residential', 'uses', 'group parking facilities', 'curb level', 'public parking
  garage', 'automated parking facilities', 'building segments', 'building(s)', 'zoning lots abutting',
  'residences developed', 'enlarged', 'residences', 'floor area', 'residential uses', 'dwelling units',
  'buildings developed', 'qualifying rooftop greenhouse', 'fully electrified building', 'ultra low
  energy building', 'multiple dwelling residences', 'Quality Housing buildings'. (The list is the set of
  bold-italic term spans inside the exclusion items, so inflected/case variants such as 'cellar'/'Cellar'
  appear as they are marked on the page.) 'qualifying exterior wall thickness' IS captured by this task.

### Group B — ZR 23-xx sections (completeness channel print/PDF = HTTP 200; cross_check result = match)

HTML channel per section: `…/article-ii/chapter-3/<section>`, HTTP 200. Print/PDF per section:
`entityprint/pdf/node/<node>` → `print/pdf/node/<node>`, HTTP 200, application/pdf. PDF generation banner
on every one: "File generated by https://zr.planning.nyc.gov on 10/6/2026" (US-Eastern generation date =
the same instant as the UTC 2026-10-07 retrieval; recorded verbatim, reconciled in a note). PDF stamp on
every one: "LAST AMENDED 12/5/2024". All read 2026-10-07. Each section's own field--name-body text was
extracted programmatically (defined terms → #term#; list labels (a)/(1)/(i) from the list markup) and
compared character-for-character with the PDF text (whitespace and non-breaking spaces removed on both
sides): IDENTICAL for all seven.

| snapshot_id | title | node | HTML bytes / sha256 | PDF bytes / sha256 | excerpt bytes | content_digest | cross_check |
|---|---|---|---|---|---|---|---|
| zr-23-23 | Special Floor Area Provisions for Multiple Dwelling Residences | 22754 | 113064 / 35e7e678… | 53389 / bbe29e9b… | 1147 | 6dd17af02303… | match |
| zr-23-231 | Floor area provisions for amenities | 17502 | 112410 / f84b6666… | 47318 / 9e71d62c… | 795 | 81eb95e85b33… | match |
| zr-23-232 | Floor area provisions for corridors | 17503 | 113416 / 980e430e… | 48121 / eba7767d… | 1632 | 0a79cda6656d… | match |
| zr-23-233 | Floor area provisions for refuse storage and disposal | 17501 | 111684 / 5e9e0de0… | 45343 / 7eb861d1… | 279 | 36b8c7da8a4d… | match |
| zr-23-234 | Elevated Ground Floor Units | 17500 | 112088 / 3f8dcbed… | 45992 / 209daaf0… | 545 | ca3481a956bc… | match |
| zr-23-342 | Rear yard requirements | 18051 | 114407 / de83aa23… | 49536 / b9a3f31f… | 2033 | 1fece3442027… | match |
| zr-23-363 | Special rules for certain interior or through lots | 18020 | 85371 / ccf92984… | 50960 / eadbe260… | 2035 | 7ff320d2f18f… | match |

Notes on Group B:
- The "23-23" page (node 22754) is the parent; its print/PDF prints the whole 23-23 family. The capture
  holds only the 23-23 lead-in (its own field--name-body), which equals the PDF portion before "23-231"
  character-for-character. The four subsections 23-231…234 are captured separately from their own leaf
  pages/PDFs.
- Official-text quirks were preserved verbatim (same ones the helper flagged): 23-231 "but not be
  limited to"; 23-232 "within common space along such corridor that accessible to residents" (missing
  "is"); 23-342 "in accordance with this Section., except" (double punctuation).

## What was NOT captured, and why
- The §12-10 whole-page print/PDF (node 18523) — HTTP 504 twice (retried). Documented fallback to the
  canonical HTML channel, as the accepted zr-12-10 capture already does. Consequence: the Resolution's
  exact list-marker glyphs for the 12-10 term lists (floor area, qualifying exterior wall thickness)
  could not be confirmed; the labels used are markup-position labels, fully disclosed. No text content is
  missing — every word of each definition is present (self-checked against the raw HTML bytes).
- Per-term 12-10 node pages and their print/PDF — HTTP 403 (not directly reachable); the term text lives
  only inside the whole-page HTML, which is the pinned channel.
- The "through lot" diagram image and its "THROUGH LOT" caption label — omitted as a figure (not
  Resolution text), disclosed in the capture notes. No other figures occur in the captured terms.
- The other 12-10 defined terms named inside the floor-area exclusions — LISTED (per R403), not captured,
  as the task directs.
- No derived number, no rule, no interpretation of any text for a lot — out of scope for a capture by
  design (task rule and S2).

## Comparison with the research helper's reading of 2026-10-06 (RQ006/007/008) — every difference, none resolved silently
The helper read only ITEM 1 (23-23 and 23-231…234) and ITEM 2 (12-10 "floor area", plus a passing mention
of "qualifying exterior wall thickness"). It did NOT read: 23-342, 23-363, 12-10 "lot, corner/interior/
through", "lot area", or "special density areas" — for those there is no helper reading to compare.

Differences and agreements where the helper did read:
- General: the helper returned SUMMARIES/partial quotes; these captures are FULL verbatim text. That is a
  difference in completeness, not in wording.
- 23-231: the helper noted the text says "laundry facilities" (unqualified), while the owner's reviewer
  had written "qualifying laundry facilities". The capture confirms the unqualified "laundry facilities"
  and preserves the official "including, but not be limited to" quirk. Agreement with the helper; the
  reviewer-summary wording "qualifying" is not in the text.
- 23-232: the helper summarised two 50% paths and quoted "that accessible to residents". The capture has
  the full text with labels (a)/(b), (1)/(2)/(3), (i)/(ii)/(iii) and preserves "that accessible to
  residents". Agreement; the capture adds the full structure the helper summarised.
- 23-233, 23-234: helper quotes match the capture verbatim.
- 12-10 floor area: the helper listed includes (1)–(12) and described the "key" exclusion items only
  (cellar, bulkheads, mechanical, parking, balconies/terraces, qualifying wall thickness, energy, and the
  §23-23 cross-reference). The capture carries ALL 17 exclusion items, including ones the helper did not
  enumerate: "uncovered steps"; "attic space … less than eight feet"; "open or roofed bridges, breeze
  ways or porches"; the stairwell exclusions for buildings >125 ft and ≥420 ft; the FDNY §511.7 storage
  exclusion; "qualifying rooftop greenhouse"; "sun control device"; and "Quality Housing buildings …
  prior to December 5, 2024". This is additional completeness, not a conflict. The helper's point that
  §12-10 does NOT itself name "laundry or storage rooms" is confirmed (they reach §12-10 only through the
  §23-23 cross-reference, which is exclusion item (16)). The helper's amendment date 12/5/2024 matches.
- 12-10 qualifying exterior wall thickness: the helper only referenced it inside floor area ("its
  conditions live in that term"). The capture holds the full term, including its two conditions
  ("over-cladding"/"re-cladding") and the historical self-reference "paragraph (12)(ii) of the definition
  of floor area in effect at the time of construction". No conflict.
- No helper difference was resolved by silently changing captured text; captured text equals the official
  page (Group B confirmed against the PDF; Group A self-checked word-for-word against the HTML).

## Checks (each run with its DIRECT exit code; venv `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`)
- (a) `python -m ruff check .` (from services/api) → "All checks passed!" — exit 0.
- (b) `python scripts/sync_zr_snapshots.py --check` (from services/api) → "OK: runtime-bundled ZR
  snapshots are byte-identical to the canonical source (37 file(s))." — exit 0. (The write pass
  `sync_zr_snapshots.py` produced the 14 bundled copies first.)
- (c) `python -m pytest -q -p no:cacheprovider tests/rules/test_zr_snapshot_bundle.py
  tests/rules/test_zoning_rule_review_register.py` (from services/api, PYTHONPATH=services/api) →
  "50 passed in 0.98s" — exit 0. (Bundle test loads every snapshot via SnapshotStore and re-verifies each
  content_digest; the review-register test is untouched and still passes — S5.)
- (d) from repo root: `python3 scripts/lanes/check_lane_paths.py --coverage` → "LANE COVERAGE PASS: 8807
  file(s)…" — exit 0; `python3 tools/modularity_check.py --check` → "selected 715 files; failures 0;
  warnings 29" — exit 0 (all 29 warnings are pre-existing python modules I did not touch; no JSON data
  file is flagged).
- (e) `git diff --cached --name-status f21ea5bb… -- docs/research/zr-snapshots/v1` → 14 lines, all `A`
  (added files only) — exit 0. Full staged scope vs claim head = the same 14 canonical captures + their 14
  byte-identical bundled copies, all `A`; no existing file modified (S5, S8).
- NOT run (by instruction): the full `services/api` pytest suite — the orchestrator runs it alone at the
  final candidate.

## Acceptance-scenario self-assessment
- S1 (each named text captured): yes — 5 lot/area/density terms + floor area + qualifying exterior wall
  thickness + 23-23/231/232/233/234 + 23-342 + 23-363. Nothing named is missing.
- S2 (source text only): yes — verbatim text + address + channel + time + amendment date; no rule, no
  per-lot reading, no derived number; notes assert only what the channel supports.
- S3 (text equals the official page): Group B proven identical to the PDF; Group A self-checked word-for-
  word against the pinned HTML. Digests recompute (loader verified in check c). Amendment dates recorded
  from each page's own stamp. The independent reviewer re-reads each page to confirm.
- S4 (complete, not excerpted where it matters): floor area complete (every includes and excludes item);
  23-23 with all four subsections each complete. No block is marked as an excerpt (none is one); figures
  are the only omissions and are disclosed.
- S5 (existing captures untouched): yes — git shows only 28 `A` additions; zr-12-10 and every other
  existing capture unchanged; the review-register check still passes.
- S6 (synced copy + bundle check): yes — 14 bundled copies byte-identical; bundle pytest passes.
- S7 (compared with helper's reading): done above, every difference listed.
- S8 (scope): only allowed_paths changed; ruff + the two targeted suites pass; full api suite left to the
  orchestrator.

## Assumptions / limitations / doubts (disclosed)
1. 12-10 list-marker glyphs: not confirmable because the §12-10 print/PDF is 504. The labels in the
   floor-area and qualifying-wall-thickness captures are markup-position labels (disclosed in each
   capture's composition and notes), not confirmed official glyphs. The item TEXT is verbatim and
   complete. If the reviewer wants confirmed glyphs, the only source is a future successful §12-10
   print/PDF fetch.
2. The floor-area "other defined terms" list in notes reflects the literal bold-italic spans, so it
   includes inflected/case variants (e.g. 'cellar'/'Cellar', 'zoning lot'/'zoning lots'). It is a
   reference list of terms named in the exclusions (R403), not a normalized glossary; each term has its
   own ZR 12-10 entry and none is captured by this task.
3. retrieved_at is recorded as the session retrieval time (2026-10-07T03:50:00Z) for every capture; the
   exact bytes are pinned by sha256/response_bytes, which is the real provenance anchor. The actual GETs
   occurred within this session shortly before that stamp.
4. raw_html_verified stays false and extraction_status stays extracted_draft on every capture (not re-read
   by a second agent). Nothing here is a Verified determination; per ADR-007 a citing rule ships under the
   standing not-professionally-reviewed label with a direct source link; professional review is advisory.
5. `test_zr_snapshot_bundle.py` was NOT edited: it discovers captures by glob (it does not list expected
   ids), so no edit is needed; the allowed-path permission for it was not used.

END-OF-REPORT
